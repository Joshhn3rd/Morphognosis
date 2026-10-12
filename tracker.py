"""
Accounts, stage pages and the daily measurement logger.

Registered on the main Flask app in app.py with:
    app.register_blueprint(tracker_bp)
"""

import csv
import io
import math
import os
import re
import secrets
from functools import wraps

from flask import (
    Blueprint, Response, abort, g, jsonify, redirect, render_template,
    request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

import db as database
import environment_content as env
import stage_config as cfg


tracker_bp = Blueprint("tracker", __name__)

MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "6"))
MAX_PASSWORD_LENGTH = 128
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def current_user():
    """The signed-in user's row, or None."""
    if "user" in g:
        return g.user
    g.user = None
    user_id = session.get("user_id")
    if user_id:
        g.user = database.get_db().one(
            "SELECT id, username FROM users WHERE id = ?", (user_id,)
        )
        if g.user is None:
            session.clear()
    return g.user


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def check_csrf():
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    expected = session.get("csrf", "")
    if not expected or not secrets.compare_digest(sent, expected):
        abort(400, description="Your page expired. Please refresh and try again.")


def api_login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            user = current_user()
        except database.DatabaseNotConfigured as exc:
            return jsonify(error=str(exc)), 503
        if user is None:
            return jsonify(error="Please sign in first."), 401
        if request.method not in ("GET", "HEAD"):
            check_csrf()
        return view(*args, **kwargs)
    return wrapper


@tracker_bp.app_context_processor
def inject_template_globals():
    try:
        user = current_user()
    except database.DatabaseNotConfigured:
        user = None
    return {
        "current_user": user,
        "csrf_token": csrf_token(),
        "stages": [cfg.STAGES[s] for s in cfg.STAGE_ORDER],
        "factors": [env.FACTORS[s] for s in env.ORDER],
    }


@tracker_bp.errorhandler(database.DatabaseNotConfigured)
def database_not_configured(exc):
    if request.path.startswith("/api/"):
        return jsonify(error=str(exc)), 503
    return render_template("auth.xhtml", mode="login", error=str(exc)), 503


# ------------------------------------------------------------
# Sign up / sign in / sign out (username + password only)
# ------------------------------------------------------------

def _safe_next(target):
    """Only allow redirects back to a path on this site."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("home")


@tracker_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth.xhtml", mode="signup", error=None,
                               min_length=MIN_PASSWORD_LENGTH)

    check_csrf()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    error = None
    if not USERNAME_RE.match(username):
        error = "Username must be 3-30 characters: letters, numbers, dot, dash or underscore."
    elif len(password) < MIN_PASSWORD_LENGTH:
        error = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    elif len(password) > MAX_PASSWORD_LENGTH:
        error = f"Password must be at most {MAX_PASSWORD_LENGTH} characters."
    elif password != confirm:
        error = "The two passwords do not match."

    if error is None:
        db = database.get_db()
        try:
            db.execute(
                "INSERT INTO users (username, username_key, password_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (username, username.lower(), generate_password_hash(password),
                 database.now_iso()),
            )
            db.commit()
        except database.integrity_errors():
            db.rollback()
            error = "That username is already taken. Please choose another."

    if error:
        return render_template("auth.xhtml", mode="signup", error=error,
                               username=username, min_length=MIN_PASSWORD_LENGTH), 400

    user = database.get_db().one(
        "SELECT id FROM users WHERE username_key = ?", (username.lower(),)
    )
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True
    return redirect(url_for("home"))


@tracker_bp.route("/login", methods=["GET", "POST"])
def login():
    nxt = _safe_next(request.values.get("next"))
    if request.method == "GET":
        return render_template("auth.xhtml", mode="login", error=None, next=nxt)

    check_csrf()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = database.get_db().one(
        "SELECT id, password_hash FROM users WHERE username_key = ?",
        (username.lower(),),
    )
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("auth.xhtml", mode="login", username=username,
                               next=nxt,
                               error="Wrong username or password."), 401

    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True
    return redirect(nxt)


@tracker_bp.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


# ------------------------------------------------------------
# Environmental factor pages (Sunlight / Temperature / Water)
# ------------------------------------------------------------

@tracker_bp.route("/environment/<slug>")
def environment_detail(slug):
    factor = env.FACTORS.get(slug)
    if factor is None:
        abort(404)
    i = env.ORDER.index(slug)
    return render_template(
        "environment_detail.xhtml",
        factor=factor,
        prev_factor=env.FACTORS[env.ORDER[i - 1]],
        next_factor=env.FACTORS[env.ORDER[(i + 1) % len(env.ORDER)]],
    )


# ------------------------------------------------------------
# Stage pages
# ------------------------------------------------------------

@tracker_bp.route("/stage/<slug>")
def stage_page(slug):
    stage = cfg.STAGES.get(slug)
    if stage is None:
        abort(404)
    return render_template(
        "stage.xhtml",
        stage=stage,
        rows=cfg.RECOMMENDATIONS[slug],
        fields=cfg.FIELDS,
        days=range(1, cfg.DAYS_PER_WEEK + 1),
        placeholders=cfg.VALUES_ARE_PLACEHOLDERS,
    )


# ------------------------------------------------------------
# Measurement logging API
# ------------------------------------------------------------

def _parse_entry(data):
    """Validate one day's measurements. Returns (values, error)."""
    values = {}
    for field in cfg.FIELDS:
        raw = data.get(field["key"])
        label = field["label"]
        if raw is None or str(raw).strip() == "":
            return None, f"{label} is required."
        try:
            number = float(str(raw).strip())
        except ValueError:
            return None, f"{label} must be a number."
        if not math.isfinite(number):
            return None, f"{label} must be a number."
        if field["kind"] == "int":
            if number != int(number):
                return None, f"{label} must be a whole number."
            number = int(number)
        if number < field["min"] or number > field["max"]:
            return None, (f"{label} must be between {field['min']} and "
                          f"{field['max']} {field['unit']}".strip() + ".")
        values[field["key"]] = number
    return values, None


def _entries_for(user_id, weeks):
    placeholders = ",".join("?" for _ in weeks)
    return database.get_db().all(
        f"SELECT week, day, {', '.join(cfg.FIELD_KEYS)}, updated_at "
        f"FROM daily_logs WHERE user_id = ? AND week IN ({placeholders}) "
        "ORDER BY week, day",
        (user_id, *weeks),
    )


def _weekly_summary(entries, weeks):
    summary = []
    for week in weeks:
        rows = [e for e in entries if e["week"] == week]
        item = {"week": week, "daysLogged": len(rows), "daysTotal": cfg.DAYS_PER_WEEK,
                "averages": {}}
        for key in cfg.FIELD_KEYS:
            item["averages"][key] = (
                round(sum(r[key] for r in rows) / len(rows), 2) if rows else None
            )
        water = item["averages"]["water"]
        item["weeklyWaterEstimate"] = round(water * cfg.DAYS_PER_WEEK) if water is not None else None
        summary.append(item)
    return summary


@tracker_bp.route("/api/logs/<slug>", methods=["GET"])
@api_login_required
def get_logs(slug):
    stage = cfg.STAGES.get(slug)
    if stage is None:
        return jsonify(error="Unknown stage."), 404
    entries = _entries_for(current_user()["id"], stage["weeks"])
    return jsonify(entries=entries, summary=_weekly_summary(entries, stage["weeks"]))


@tracker_bp.route("/api/logs/<int:week>/<int:day>", methods=["PUT"])
@api_login_required
def save_log(week, day):
    if week not in cfg.ALL_WEEKS:
        return jsonify(error="Week is out of range."), 400
    if not 1 <= day <= cfg.DAYS_PER_WEEK:
        return jsonify(error="Day must be 1 to 7."), 400

    data = request.get_json(silent=True) or {}
    values, error = _parse_entry(data)
    if error:
        return jsonify(error=error), 400

    db = database.get_db()
    user_id = current_user()["id"]
    now = database.now_iso()
    columns = cfg.FIELD_KEYS
    assignments = ", ".join(f"{c} = ?" for c in columns)
    updated = db.execute(
        f"UPDATE daily_logs SET {assignments}, updated_at = ? "
        "WHERE user_id = ? AND week = ? AND day = ?",
        (*[values[c] for c in columns], now, user_id, week, day),
    )
    if updated.rowcount == 0:
        db.execute(
            f"INSERT INTO daily_logs (user_id, week, day, {', '.join(columns)}, updated_at) "
            f"VALUES (?, ?, ?, {', '.join('?' for _ in columns)}, ?)",
            (user_id, week, day, *[values[c] for c in columns], now),
        )
    db.commit()

    stage = cfg.STAGES[cfg.stage_for_week(week)]
    entries = _entries_for(user_id, stage["weeks"])
    return jsonify(saved=True, entries=entries,
                   summary=_weekly_summary(entries, stage["weeks"]))


@tracker_bp.route("/api/logs/<int:week>/<int:day>", methods=["DELETE"])
@api_login_required
def delete_log(week, day):
    if week not in cfg.ALL_WEEKS or not 1 <= day <= cfg.DAYS_PER_WEEK:
        return jsonify(error="Week or day is out of range."), 400
    db = database.get_db()
    user_id = current_user()["id"]
    db.execute(
        "DELETE FROM daily_logs WHERE user_id = ? AND week = ? AND day = ?",
        (user_id, week, day),
    )
    db.commit()
    stage = cfg.STAGES[cfg.stage_for_week(week)]
    entries = _entries_for(user_id, stage["weeks"])
    return jsonify(deleted=True, entries=entries,
                   summary=_weekly_summary(entries, stage["weeks"]))


@tracker_bp.route("/api/export.csv", methods=["GET"])
@api_login_required
def export_csv():
    entries = _entries_for(current_user()["id"], cfg.ALL_WEEKS)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["stage", "week", "day", *cfg.FIELD_KEYS, "saved_at"])
    for e in entries:
        writer.writerow([cfg.stage_for_week(e["week"]), e["week"], e["day"],
                         *[e[k] for k in cfg.FIELD_KEYS], e["updated_at"]])
    out.write("\n")
    writer = csv.writer(out)
    writer.writerow(["WEEKLY AVERAGES"])
    writer.writerow(["stage", "week", "days_logged", *[f"avg_{k}" for k in cfg.FIELD_KEYS]])
    for s in _weekly_summary(entries, cfg.ALL_WEEKS):
        if s["daysLogged"]:
            writer.writerow([cfg.stage_for_week(s["week"]), s["week"], s["daysLogged"],
                             *[s["averages"][k] for k in cfg.FIELD_KEYS]])
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=morphognosis_measurements.csv"},
    )

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)

WAITLIST_FILE = os.path.join(os.path.dirname(__file__), "waitlist.json")


def load_waitlist():
    if not os.path.exists(WAITLIST_FILE):
        return []
    with open(WAITLIST_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_waitlist(entries):
    with open(WAITLIST_FILE, "w") as f:
        json.dump(entries, f, indent=2)


@app.route("/")
def index():
    count = len(load_waitlist())
    return render_template("index.html", waitlist_count=count)


@app.route("/waitlist", methods=["POST"])
def join_waitlist():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    waitlist = load_waitlist()

    if any(e["email"] == email for e in waitlist):
        return jsonify({"success": False, "message": "You're already on the waitlist! We'll be in touch."}), 200

    waitlist.append({
        "email": email,
        "joined_at": datetime.now(timezone.utc).isoformat(),
    })
    save_waitlist(waitlist)

    position = len(waitlist)
    return jsonify({
        "success": True,
        "message": f"You're #{position} on the waitlist — we'll email you at launch!",
        "position": position,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)

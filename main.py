

# Merlin Auth Server — Flask Backend
# ----------------------------------
# This Flask application provides user authentication and goal management services for Merlin AI.
# It integrates with Supabase to handle user sign-up, login, password reset, and personalized goal storage.

import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import os
import sys

# Initialize Flask app
app = Flask(__name__)

# Load Supabase environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Health check route to verify the server is running
@app.route("/")
def home():
    return "Merlin Auth Server is live."

# ------------------- Auth Routes -------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    display_name = data.get("display_name", "")

    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"display_name": display_name}
            }
        })
        return jsonify({
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "created_at": result.user.created_at,
                "aud": result.user.aud,
                "role": result.user.role
            },
            "session": {
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token,
                "expires_in": result.session.expires_in,
                "token_type": result.session.token_type
            },
            "display_name": display_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if not result.user or not result.session:
            return jsonify({"error": "Invalid email or password"}), 401

        display_name = result.user.user_metadata.get("display_name", "")
        return jsonify({
            "user": {
                "id": result.user.id,
                "email": result.user.email,
                "created_at": result.user.created_at,
                "aud": result.user.aud,
                "role": result.user.role
            },
            "session": {
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token,
                "expires_in": result.session.expires_in,
                "token_type": result.session.token_type
            },
            "display_name": display_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        supabase.auth.reset_password_email(email)
        return "", 204
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ------------------- Preferences -------------------
@app.route("/set-preferences", methods=["POST"])
def set_preferences():
    data = request.json
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id

        # Upsert preferences
        preferences = {
            "user_id": user_id,
            "personality_mode": data.get("personality_mode"),
            "tone_preference": data.get("tone_preference"),
            "allow_reflection": data.get("allow_reflection"),
            "humor_enabled": data.get("humor_enabled")
        }

        supabase.table("preferences").upsert(preferences, on_conflict=["user_id"]).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-preferences", methods=["GET"])
def get_preferences():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        result = supabase.table("preferences").select("*").eq("user_id", user_id).execute()
        if result.data:
            return jsonify(result.data[0])
        else:
            return jsonify({"preferences": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------- Commitment Tracking -------------------
@app.route("/get-commitments", methods=["GET"])
def get_commitments():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        result = supabase.table("commitments").select("*").eq("user_id", user_id).order("due_date", desc=False).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add-commitment", methods=["POST"])
def add_commitment():
    data = request.json
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    commitment_text = data.get("commitment_text")
    due_date = data.get("due_date")

    if not commitment_text:
        return jsonify({"error": "Missing commitment text"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        payload = {
            "user_id": user_id,
            "commitment_text": commitment_text,
            "status": "pending"
        }
        if due_date:
            payload["due_date"] = due_date

        supabase.table("commitments").insert(payload).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------- Goal Management -------------------
@app.route("/set-goal", methods=["POST"])
def set_goal():
    data = request.json
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    goal_text = data.get("goal")

    if not token or not goal_text:
        return jsonify({"error": "Missing token or goal"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        existing = supabase.table("goals").select("*").eq("user_id", user_id).execute()
        if existing.data:
            supabase.table("goals").update({"goal_text": goal_text}).eq("user_id", user_id).execute()
        else:
            supabase.table("goals").insert({"user_id": user_id, "goal_text": goal_text, "status": "active"}).execute()
        return jsonify({"success": True, "goal": goal_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-goal", methods=["GET"])
def get_goal():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        result = supabase.table("goals").select("goal_text").eq("user_id", user_id).execute()
        if result.data:
            return jsonify({"goal": result.data[0]["goal_text"]})
        else:
            return jsonify({"goal": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run app


@app.route('/latest-session-summary', methods=['GET'])
def latest_session_summary():
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        supabase.auth.sign_in_with_token(token)
        user = supabase.auth.get_user()
        user_id = user.user.id

        result = (
            supabase.table("session_logs")
            .select("summary")
            .eq("user_id", user_id)
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        )

        if result.data:
            return jsonify({"summary": result.data[0]["summary"]})
        else:
            return jsonify({"summary": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# 🧠 Save session summary and full chat log

@app.route("/save-session", methods=["POST"])
def save_session():
    data = request.json
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    print(">>> Saving session log...", file=sys.stderr); sys.stderr.flush()
    print("Token:", token, file=sys.stderr); sys.stderr.flush()
    print("Summary:", data.get("summary", "")[:60], file=sys.stderr); sys.stderr.flush()
    print("Full log entries:", len(data.get("full_log", [])), file=sys.stderr); sys.stderr.flush()

    if not token or not data.get("summary") or not data.get("full_log"):
        return jsonify({"error": "Missing token, summary, or full_log"}), 400

    try:
        user_id = supabase.auth.get_user(token).user.id
        print("User ID:", user_id, file=sys.stderr); sys.stderr.flush()

        supabase.table("session_logs").insert({
            "user_id": user_id,
            "summary": data["summary"],
            "full_log": json.dumps(data["full_log"]),
            "started_at": datetime.utcnow().isoformat()
        }).execute()

        print("✅ Session log inserted successfully.", file=sys.stderr); sys.stderr.flush()
        return jsonify({"success": True})

    except Exception as e:
        print("⚠️ Error saving session log:", str(e), file=sys.stderr); sys.stderr.flush()
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

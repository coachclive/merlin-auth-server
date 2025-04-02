from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return "Merlin Auth Server is live."

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
<<<<<<< HEAD
=======
        if not result.user or not result.session:
            return jsonify({"error": "Invalid email or password"}), 401

>>>>>>> a76769b (Add /reset-password route)
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

<<<<<<< HEAD
=======
    try:
        supabase.auth.reset_password_email(email)
        return "", 204  # No content = success
    except Exception as e:
        return jsonify({"error": str(e)}), 400

>>>>>>> a76769b (Add /reset-password route)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return "Merlin Auth Server is alive."

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
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        user_data = {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at,
            "aud": response.user.aud,
            "role": response.user.role
        }

        session_data = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "token_type": response.session.token_type
        }

        return jsonify({
            "user": user_data,
            "session": session_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

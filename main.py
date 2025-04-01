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
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        return jsonify({
            "user": result.user,
            "session": result.session
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

        session_data = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "token_type": response.session.token_type
        }

        return jsonify({
            "user": response.user,
            "session": session_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

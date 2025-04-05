# Merlin Auth Server

This is the backend authentication API for the Merlin AI coaching chatbot. It provides endpoints for user login and goal retrieval, simulating connection to a Supabase backend.

## 🚀 Features
- `/login` route for authenticating users (mocked)
- `/get-goal` route for retrieving the user's active coaching goal

## 📦 Requirements
- Python 3.8+
- Flask

Install Flask using pip:
```bash
pip install Flask
```

## 🔧 Environment Setup
No external config or secrets are required for this mock version.

For a production version, you’d need:
- Supabase URL and API key
- Database connection

## 🧪 Running Locally
```bash
python app.py
```
This will start the server at `http://127.0.0.1:5000`

## 🔁 Endpoints

### `POST /login`
Accepts:
```json
{
  "email": "user@example.com",
  "password": "secret"
}
```
Returns a mock session and user object.

### `GET /get-goal`
Requires `Authorization: Bearer <token>` header.
Returns:
```json
{
  "goal": "Become a better listener"
}
```

## 📁 File Structure
- `app.py` — main Flask server with routes
- `README.md` — this file

## 🛠 Future Plans
- Replace mocked login with real Supabase integration
- Store and update goals per authenticated user
- Add routes for commitments and preferences

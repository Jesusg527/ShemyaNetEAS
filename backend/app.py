from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# -----------------------------------
# ENV
# -----------------------------------
TOKEN_URL = os.getenv("Token_URL")
TRANSACTION_URL = os.getenv("transaction_URL")

ORG_ID = os.getenv("ORG_ID")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")

# -----------------------------------
# TOKEN CACHE
# -----------------------------------
_cached_token = None
_token_time = 0
TOKEN_TTL = 3300  # ~55 minutes


# -----------------------------------
# NORMALIZE MAC/IP
# -----------------------------------
def normalize(value):
    return (value or "").replace(":", "").replace("-", "").lower()


# -----------------------------------
# GET TOKEN
# -----------------------------------
def get_token():

    global _cached_token, _token_time

    if _cached_token and (time.time() - _token_time) < TOKEN_TTL:
        return _cached_token

    payload = {
        "orgId": ORG_ID,
        "userId": USER_ID,
        "password": PASSWORD
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            TOKEN_URL,
            json=payload,
            headers=headers,
            timeout=15
        )

        print("TOKEN STATUS:", response.status_code)

        if response.status_code != 200:
            print("TOKEN ERROR:", response.text)
            return None

        data = response.json()

        token = data.get("token") or data.get("accessToken")

        if not token:
            print("NO TOKEN RETURNED")
            return None

        _cached_token = token
        _token_time = time.time()

        print("TOKEN RECEIVED + CACHED")

        return token

    except Exception as e:
        print("TOKEN ERROR:", e)
        return None


# -----------------------------------
# HOME
# -----------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Backend running"})


# -----------------------------------
# LOOKUP TRANSACTIONS
# -----------------------------------
@app.route("/lookup", methods=["POST"])
def lookup():

    try:
        body = request.json or {}

        search = normalize(body.get("search", "").strip())
        date = body.get("date")

        if not search:
            return jsonify({"error": "Search required"}), 400

        if not date:
            return jsonify({"error": "Date required"}), 400

        token = get_token()

        if not token:
            return jsonify({"error": "Token generation failed"}), 500

        # IMPORTANT: consistent auth format
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        params = {
            "transactionDatetime": date,
            "limit": 200
        }

        response = requests.get(
            TRANSACTION_URL,
            headers=headers,
            params=params,
            timeout=15
        )

        print("REQUEST URL:", response.url)
        print("STATUS:", response.status_code)

        # retry once on 401
        if response.status_code == 401:
            print("TOKEN EXPIRED — RETRYING ONCE...")

            token = get_token()

            headers["Authorization"] = token

            response = requests.get(
                TRANSACTION_URL,
                headers=headers,
                params=params,
                timeout=15
            )

        if response.status_code != 200:
            print("API ERROR:", response.text)
            return jsonify({"error": response.text}), response.status_code

        api_data = response.json()
        users = api_data.get("data", {}).get("user", [])

        results = []

        # -----------------------------------
        # SEARCH FILTER (MAC + IP)
        # -----------------------------------
        for user in users:

            mac = normalize(user.get("macAddress"))
            ip = (user.get("ipAddress") or "").lower()

            if search in mac or search in ip:
                results.append(user)

        return jsonify({"results": results})

    except Exception as e:
        print("LOOKUP ERROR:", e)
        return jsonify({"error": str(e)}), 500


# -----------------------------------
# RUN SERVER
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
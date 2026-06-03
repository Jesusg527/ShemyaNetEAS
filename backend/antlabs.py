
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ORG_ID = os.getenv("ORG_ID")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
TOKEN_URL = os.getenv("TOKEN_URL")
TRANSACTION_URL = os.getenv("TRANSACTION_URL")


def get_token():
    payload = {
        "orgId": ORG_ID,
        "userId": USER_ID,
        "password": PASSWORD
    }

    response = requests.post(
        TOKEN_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    token = data.get("token") or data.get("accessToken")

    if not token:
        raise Exception("Token not found")

    return token


def get_transactions(search, date):
    token = get_token()

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

    response.raise_for_status()

    data = response.json()

    users = data.get("data", {}).get("user", [])

    results = []

    for user in users:
        mac = (user.get("macAddress") or "").lower()
        ip = (user.get("ipAddress") or "").lower()

        if search.lower() in mac or search.lower() in ip:
            results.append({
                "userId": user.get("userId"),
                "macAddress": user.get("macAddress"),
                "ipAddress": user.get("ipAddress"),
                "billingId": user.get("billingId"),
                "planName": user.get("planName"),
                "amount": user.get("amount"),
                "transactionDatetimeLocal": user.get("transactionDatetimeLocal"),
                "transactionId": user.get("transactionId")
            })

    return results





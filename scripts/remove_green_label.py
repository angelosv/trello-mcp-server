#!/usr/bin/env python3
"""Remove the empty green label from Kotlin SDK cards."""
import os
import httpx

# Load .env
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                v = v.strip().strip('"').strip("'")
                if k == 'TRELLO_API_KEY':
                    os.environ['TRELLO_API_KEY'] = v
                elif k == 'TRELLO_API_TOKEN' or k == 'TRELLO_TOKEN':
                    os.environ['TRELLO_TOKEN'] = v
except FileNotFoundError:
    pass

KEY = os.getenv("TRELLO_API_KEY", "e582f14026a35a1b1a886d0ba2ad2316")
TOKEN = os.getenv("TRELLO_API_TOKEN") or os.getenv("TRELLO_TOKEN")

GREEN_LABEL = '6964ea21570279f07def77f3'
CARDS = [
    '698c9fd83f99805c8c9f9aa3',
    '698c9fdae330005d5a70b42f',
    '698c9fd9c22d4db824670b94',
    '698c9fd98c41f184f2a46f93',
    '698c9fdba6a57f8f814f2169',
]

def main():
    if not TOKEN:
        print("❌ TRELLO_API_TOKEN o TRELLO_TOKEN requerido en .env")
        return
    for card_id in CARDS:
        url = f"https://api.trello.com/1/cards/{card_id}/idLabels/{GREEN_LABEL}"
        r = httpx.delete(url, params={"key": KEY, "token": TOKEN})
        if r.status_code == 200:
            print(f"✓ Removed green label from card {card_id}")
        else:
            print(f"✗ Failed {card_id}: {r.status_code} {r.text[:100]}")

if __name__ == "__main__":
    main()

import os, requests
r = requests.post("https://api.intra.42.fr/oauth/token", data={
    "grant_type": "client_credentials",
    "client_id": os.environ["FT_CLIENT_ID"],
    "client_secret": os.environ["FT_CLIENT_SECRET"]})
t = r.json()["access_token"]
s = requests.get("https://api.intra.42.fr/v2/users/azmakhlo/locations_stats",
    headers={"Authorization": f"Bearer {t}"},
    params={"begin_at": "2026-09-01", "end_at": "2026-09-30"})
print(s.status_code)
print(s.text)

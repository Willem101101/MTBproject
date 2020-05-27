import requests

url = "https://www.strava.com/api/v3/athletes/51414134/stats"

headers = {"Authorization": "Bearer " + "11f13af3b45250ec447aff7aaf4a05ce9f46651a"}
params = {"include_all_efforts": "true"}

activity = requests.get(url, headers=headers).json()

print(activity)

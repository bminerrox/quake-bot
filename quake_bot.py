import requests
import tweepy
import time
import os

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

posted_ids = set()

def fetch_quakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/6.0_hour.geojson"
    try:
        res = requests.get(url, timeout=10)
        return res.json().get("features", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def create_tweet(quake):
    props = quake["properties"]
    mag = props["mag"]
    place = props["place"]
    time_utc = time.strftime('%H:%M UTC (%b %d)', time.gmtime(props["time"] / 1000))
    coords = quake["geometry"]["coordinates"]
    return (
        f"🌍 M{mag:.1f} Earthquake — {place}\n"
        f"📍 Lat: {coords[1]:.2f}, Long: {coords[0]:.2f}\n"
        f"🕒 {time_utc}\n"
        f"#earthquake #USGS"
    )

while True:
    for quake in fetch_quakes():
        quake_id = quake["id"]
        if quake_id not in posted_ids:
            try:
                tweet = create_tweet(quake)
                api.update_status(tweet)
                print("Tweeted:", tweet)
                posted_ids.add(quake_id)
            except Exception as e:
                print("Tweet error:", e)
    time.sleep(300)

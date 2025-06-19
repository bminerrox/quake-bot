import os
os.environ["PORT"] = "10000"  # Explicitly tell Render which port to scan

import requests
import tweepy
import time
import socket
import threading

# Start dummy web server so Render sees an open port
def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    sock = socket.socket()
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    print(f"✅ Dummy web server running on port {port}")

threading.Thread(target=keep_alive).start()  # Start early to beat Render's scan

# Load Twitter API keys from Render environment variables
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

# Set up Twitter client
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Track already-posted quake IDs
posted_ids = set()

# Fetch earthquakes from USGS
def fetch_quakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
    try:
        res = requests.get(url, timeout=10)
        return res.json().get("features", [])
    except Exception as e:
        print(f"❌ Error fetching quake data: {e}")
        return []

# Format tweet
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

# Main loop
print("🚀 Earthquake bot is running...")
while True:
    for quake in fetch_quakes():
        quake_id = quake["id"]
        if quake_id not in posted_ids:
            try:
                tweet = create_tweet(quake)
                api.update_status(tweet)
                print(f"✅ Tweeted: {tweet}")
                posted_ids.add(quake_id)
            except Exception as e:
                print(f"❌ Tweet error: {e}")
    time.sleep(300)  # Wait 5 minutes before checking again

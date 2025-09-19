from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from langdetect import detect
import requests
import os
import re

app = Flask(__name__)

# Load OpenWeatherMap API key from environment variable
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# List of cities supported
CITY_LIST = ["Chennai", "Delhi", "Mumbai", "Hyderabad", "Bangalore", "Kolkata", "Pune", "Lucknow", "Jaipur"]

def extract_city(text):
    """Extract city name from text (case-insensitive, robust to extra words)."""
    text = text.lower()
    for city in CITY_LIST:
        if city.lower() in text:
            return city
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_query = data.get("queryResult", {}).get("queryText", "")

        # Detect user's language
        user_lang = detect(user_query)

        # Translate query to English
        translated_query = GoogleTranslator(source="auto", target="en").translate(user_query)

        # Detect city
        city = extract_city(translated_query)
        if not city:
            reply = "Please tell me which city you want the weather for."
        else:
            # Fetch weather data from OpenWeatherMap
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url).json()

            if response.get("cod") != 200:
                reply = f"Sorry, I could not find the weather for {city}."
            else:
                temp = response["main"]["temp"]
                condition = response["weather"][0]["description"]
                reply = f"The weather in {city} is {temp}°C with {condition}."

        # Translate reply back to user's language if not English
        if user_lang != "en":
            final_reply = GoogleTranslator(source="en", target=user_lang).translate(reply)
        else:
            final_reply = reply

        return jsonify({"fulfillmentText": final_reply})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

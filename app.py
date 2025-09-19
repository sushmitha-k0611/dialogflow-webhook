from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
import requests
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = Flask(__name__)

# Pre-load a few common cities (expand as needed)
CITY_LIST = ["Chennai", "Delhi", "Mumbai", "Hyderabad", "Bangalore",
             "Kolkata", "Pune", "Lucknow", "Jaipur"]

def extract_city(text):
    """Extract city name from text using a simple match."""
    for city in CITY_LIST:
        if re.search(city, text, re.IGNORECASE):
            return city
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_query = data["queryResult"]["queryText"]

        # Detect original language
        user_lang = GoogleTranslator().detect(user_query)

        # Translate query to English
        translated_query = GoogleTranslator(source="auto", target="en").translate(user_query)

        # Detect city
        city = extract_city(translated_query)
        if not city:
            reply = "Please tell me which city you want the weather for."
            final_reply = GoogleTranslator(source="en", target=user_lang).translate(reply)
            return jsonify({"fulfillmentText": final_reply})

        # Fetch weather data
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            reply = f"Sorry, I could not find the weather for {city}."
        else:
            temp = response["main"]["temp"]
            condition = response["weather"][0]["description"]
            reply = f"The weather in {city} is {temp}°C with {condition}."

        # Translate reply back to user's language
        final_reply = GoogleTranslator(source="en", target=user_lang).translate(reply)

        return jsonify({"fulfillmentText": final_reply})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

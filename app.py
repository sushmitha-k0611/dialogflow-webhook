from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from langdetect import detect
import requests
import re
import os

app = Flask(__name__)

# Load API key from environment variable
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Pre-load a few common cities (expand as needed)
CITY_LIST = ["Chennai", "Delhi", "Mumbai", "Hyderabad", "Bangalore", "Kolkata", "Pune", "Lucknow", "Jaipur"]

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

        # Step 1: Detect user language
        user_lang = detect(user_query)

        # Step 2: Translate user query to English
        translated_query = GoogleTranslator(source="auto", target="en").translate(user_query)

        # Step 3: Detect city
        city = extract_city(translated_query)
        if not city:
            reply = "Please tell me which city you want the weather for."
        else:
            # Step 4: Fetch weather data
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url).json()

            if response.get("cod") != 200:
                reply = f"Sorry, I could not find the weather for {city}."
            else:
                temp = response["main"]["temp"]
                condition = response["weather"][0]["description"]
                reply = f"The weather in {city} is {temp}°C with {condition}."

        # Step 5: Translate reply back to user’s language
        if user_lang != "en":  # Only translate if user language is not English
            final_reply = GoogleTranslator(source="en", target=user_lang).translate(reply)
        else:
            final_reply = reply

        return jsonify({"fulfillmentText": final_reply})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Error: {str(e)}"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)

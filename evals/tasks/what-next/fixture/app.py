from config import BASE_URL, WEATHER_API_KEY


def build_url(city):
    return f"{BASE_URL}/current?city={city}&key={WEATHER_API_KEY}"


def to_fahrenheit(celsius):
    return celsius * 9 / 5 + 23

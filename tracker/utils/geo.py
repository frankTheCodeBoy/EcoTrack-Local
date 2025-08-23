from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from tracker.models import RegionInfo
import time

MANUAL_OVERRIDES = {
    "hotu": {
        "latitude": -1.95,
        "longitude": 30.06,
        "emoji": "🇷🇼",
        "address": "Hotu, Rwanda"
    }
}

geolocator = Nominatim(user_agent="eco_tracker", timeout=10)


def iso_to_emoji(code):
    if len(code) != 2:
        return "🌍"
    return chr(
        ord(code[0].upper()) + 127397) + chr(
            ord(code[1].upper()) + 127397)


def safe_geocode(loc, retries=1):
    for attempt in range(retries + 1):
        try:
            return geolocator.geocode(loc)
        except GeocoderTimedOut:
            time.sleep(2)
    return None


def clean_location(raw):
    if not raw or raw.lower().strip() in ["none", "unknown", ""]:
        return "Unknown"
    loc = raw.strip().title()
    if loc.lower().startswith("none "):
        loc = loc[5:]
    if ',' not in loc and not loc.lower().endswith('kenya'):
        loc += ', Kenya'
    return loc


def enrich_region(name):
    if not name:
        return None

    cleaned = clean_location(name)

    if cleaned.lower() in MANUAL_OVERRIDES:
        data = MANUAL_OVERRIDES[cleaned.lower()]
        region, _ = RegionInfo.objects.get_or_create(name=name)
        region.latitude = data["latitude"]
        region.longitude = data["longitude"]
        region.emoji = data["emoji"]
        region.address = data["address"]
        region.save()
        return region

    region, created = RegionInfo.objects.get_or_create(name=name)
    if created or not region.latitude:
        geo = safe_geocode(cleaned, retries=1)
        if geo:
            region.latitude = geo.latitude
            region.longitude = geo.longitude
            region.address = geo.address
            country_code = geo.raw.get('address', {}).get('country_code', '')
            region.emoji = iso_to_emoji(country_code) if country_code else "🌍"
            region.save()
    return region

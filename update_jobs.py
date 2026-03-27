import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

HEADERS = {
    "User-Agent": "JobHunterApp/1.0"
}

TESCO_SEARCH_URL = "https://apply.tesco-careers.com/v2/job/search"
TESCO_BASE_URL = "https://apply.tesco-careers.com"

ALDI_SEARCH_URL = "https://careers.aldirecruitment.co.uk/vacancies/vacancy-search-results.aspx?view=list"

# Coventry City Centre approximate coordinates
COVENTRY_CITY_CENTRE = (52.4081, -1.5106)

geolocator = Nominatim(user_agent="job_hunter_app")

def normalize(text):
    return re.sub(r"\s+", " ", (text or "")).strip()

def get_distance_from_coventry(location_text):
    if not location_text:
        return "Distance unknown"

    try:
        place = geolocator.geocode(f"{location_text}, UK", timeout=10)
        if not place:
            return "Distance unknown"

        miles = geodesic(
            COVENTRY_CITY_CENTRE,
            (place.latitude, place.longitude)
        ).miles

        return f"{round(miles)} miles"
    except Exception:
        return "Distance unknown"

def scrape_tesco():
    jobs = []
    seen = set()

    search_url = "https://apply.tesco-careers.com/v2/job/search"
    base_url = "https://apply.tesco-careers.com"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            title = normalize(a.get_text(" ", strip=True))
            href = a["href"]

            if not title:
                continue

            if "members/modules/job/detail.php" not in href:
                continue

            full_url = urljoin(base_url, href)

            if full_url in seen:
                continue
            seen.add(full_url)

            location = "Unknown"

            # Try to get location from title after the last hyphen
            # Example: "Tesco Colleague - Bristol Business Park Express"
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    location = parts[-1].strip()

            jobs.append({
                "title": title,
                "company": "Tesco",
                "category": "retail",
                "location": location,
                "distance": "Distance unknown",
                "url": full_url
            })

    except Exception as e:
        print("Tesco scrape failed:", e)

    return jobs

def scrape_aldi():
    jobs = []
    seen = set()

    try:
        r = requests.get(ALDI_SEARCH_URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            title = normalize(a.get_text(" ", strip=True))
            href = urljoin(ALDI_SEARCH_URL, a["href"])
            combined = f"{title} {href}".lower()

            if not title:
                continue

            # Skip obvious non-job junk
            if any(bad in combined for bad in [
                "login", "privacy", "cookie", "terms", "contact",
                "about", "explore more", "placements", "graduate"
            ]):
                continue

            # Keep likely jobs
            if not any(word in combined for word in [
                "assistant", "manager", "cleaner", "warehouse",
                "transport", "apprentice", "analyst", "store"
            ]):
                continue

            key = (title, href)
            if key in seen:
                continue
            seen.add(key)

            # Aldi result pages often need extra parsing for exact city,
            # so we start with unknown and improve later if needed.
            location = "Unknown"
            distance = "Distance unknown"

            jobs.append({
                "title": title,
                "company": "Aldi",
                "category": "retail",
                "location": location,
                "distance": distance,
                "url": href
            })

    except Exception as e:
        print("Aldi scrape failed:", e)

    return jobs

tesco_jobs = scrape_tesco()
aldi_jobs = []

all_jobs = tesco_jobs 

with open("jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print(f"Saved {len(all_jobs)} jobs")
print(f"Tesco: {len(tesco_jobs)}")
print(f"Aldi: {len(aldi_jobs)}")
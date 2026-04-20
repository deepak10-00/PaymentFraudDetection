import httpx
import logging
from typing import Dict, Any

class GeolocationService:
    """
    Service to resolve IP addresses into geographic locations using ip-api.com.
    Includes a simple in-memory cache to stay within rate limits.
    """
    def __init__(self):
        self.cache = {}
        self.api_url = "http://ip-api.com/json/"
        self.logger = logging.getLogger(__name__)

    def get_location(self, ip: str) -> Dict[str, str]:
        if not ip or ip in ["127.0.0.1", "::1"]:
            return {"city": "Local", "state": "Local", "country": "Local"}

        if ip in self.cache:
            return self.cache[ip]

        try:
            # Using sync request for easier integration with existing sync components
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.api_url}{ip}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        result = {
                            "city": data.get("city", "N/A"),
                            "state": data.get("regionName", "N/A"),
                            "country": data.get("country", "N/A")  # Return full country name instead of countryCode
                        }
                        self.cache[ip] = result
                        return result
                    else:
                        self.logger.warning(f"GeoIP API failed for {ip}: {data.get('message')}")
        except Exception as e:
            self.logger.error(f"Error fetching geolocation for {ip}: {e}")

        return {"city": "N/A", "state": "N/A", "country": "N/A"}

# Singleton instance
geolocation_service = GeolocationService()

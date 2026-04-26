import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def geocode_address(street: str, city: str, country: str = "Colombia") -> Optional[tuple[float, float]]:
    """
    Convierte una dirección en coordenadas (lat, lng) usando Nominatim/OSM.
    Retorna None si no se encuentra la dirección.
    """
    query = f"{street}, {city}, {country}"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "DMS-App/1.0 (delivery-management-system)"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NOMINATIM_URL, params=params, headers=headers)
            response.raise_for_status()
            results = response.json()
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        logger.warning(f"Geocoding failed for '{query}': {e}")

    return None

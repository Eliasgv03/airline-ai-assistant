"""
IATA Airport Code Service

Hybrid strategy for looking up airport codes:
1. First search in local database (instant)
2. If not found, search via Amadeus API (fallback)
3. Cache Amadeus results for future lookups
"""

from typing import Any

from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Comprehensive IATA database with 150+ major airports
# Includes Spanish, Hindi, and other language variants
IATA_DATABASE: dict[str, str] = {
    # ===== INDIA (Air India primary routes) =====
    "delhi": "DEL",
    "new delhi": "DEL",
    "nueva delhi": "DEL",
    "नई दिल्ली": "DEL",
    "दिल्ली": "DEL",
    "mumbai": "BOM",
    "bombay": "BOM",
    "मुंबई": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "बेंगलुरु": "BLR",
    "chennai": "MAA",
    "madras": "MAA",
    "चेन्नई": "MAA",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "कोलकाता": "CCU",
    "hyderabad": "HYD",
    "हैदराबाद": "HYD",
    "goa": "GOI",
    "गोवा": "GOI",
    "pune": "PNQ",
    "पुणे": "PNQ",
    "ahmedabad": "AMD",
    "अहमदाबाद": "AMD",
    "jaipur": "JAI",
    "जयपुर": "JAI",
    "kochi": "COK",
    "cochin": "COK",
    "कोच्चि": "COK",
    "thiruvananthapuram": "TRV",
    "trivandrum": "TRV",
    "lucknow": "LKO",
    "लखनऊ": "LKO",
    "patna": "PAT",
    "पटना": "PAT",
    "amritsar": "ATQ",
    "अमृतसर": "ATQ",
    "srinagar": "SXR",
    "श्रीनगर": "SXR",
    "varanasi": "VNS",
    "बनारस": "VNS",
    "वाराणसी": "VNS",
    "chandigarh": "IXC",
    "indore": "IDR",
    "bhopal": "BHO",
    "nagpur": "NAG",
    "coimbatore": "CJB",
    "mangalore": "IXE",
    "visakhapatnam": "VTZ",
    "vizag": "VTZ",
    "bhubaneswar": "BBI",
    "ranchi": "IXR",
    "guwahati": "GAU",
    "imphal": "IMF",
    "agartala": "IXA",
    "port blair": "IXZ",
    "andaman": "IXZ",
    # ===== EAST ASIA =====
    "tokyo": "NRT",
    "tokio": "NRT",
    "東京": "NRT",
    "narita": "NRT",
    "haneda": "HND",
    "osaka": "KIX",
    "大阪": "KIX",
    "beijing": "PEK",
    "peking": "PEK",
    "pekín": "PEK",
    "北京": "PEK",
    "shanghai": "PVG",
    "shanghái": "PVG",
    "上海": "PVG",
    "guangzhou": "CAN",
    "canton": "CAN",
    "广州": "CAN",
    "shenzhen": "SZX",
    "深圳": "SZX",
    "hong kong": "HKG",
    "hongkong": "HKG",
    "香港": "HKG",
    "taipei": "TPE",
    "台北": "TPE",
    "seoul": "ICN",
    "seúl": "ICN",
    "서울": "ICN",
    # ===== SOUTHEAST ASIA =====
    "singapore": "SIN",
    "singapur": "SIN",
    "新加坡": "SIN",
    "kuala lumpur": "KUL",
    "bangkok": "BKK",
    "กรุงเทพ": "BKK",
    "jakarta": "CGK",
    "yakarta": "CGK",
    "manila": "MNL",
    "ho chi minh": "SGN",
    "saigon": "SGN",
    "hanoi": "HAN",
    "bali": "DPS",
    "denpasar": "DPS",
    "phuket": "HKT",
    "yangon": "RGN",
    "rangoon": "RGN",
    "phnom penh": "PNH",
    # ===== MIDDLE EAST =====
    "dubai": "DXB",
    "dubái": "DXB",
    "دبي": "DXB",
    "abu dhabi": "AUH",
    "doha": "DOH",
    "riyadh": "RUH",
    "riad": "RUH",
    "jeddah": "JED",
    "yeda": "JED",
    "muscat": "MCT",
    "mascate": "MCT",
    "kuwait": "KWI",
    "bahrain": "BAH",
    "tel aviv": "TLV",
    "amman": "AMM",
    "amán": "AMM",
    "tehran": "IKA",
    "teherán": "IKA",
    # ===== EUROPE =====
    "london": "LHR",
    "londres": "LHR",
    "लंदन": "LHR",
    "london heathrow": "LHR",
    "london gatwick": "LGW",
    "london stansted": "STN",
    "paris": "CDG",
    "parís": "CDG",
    "पेरिस": "CDG",
    "charles de gaulle": "CDG",
    "frankfurt": "FRA",
    "fráncfort": "FRA",
    "amsterdam": "AMS",
    "ámsterdam": "AMS",
    "madrid": "MAD",
    "barcelona": "BCN",
    "rome": "FCO",
    "roma": "FCO",
    "रोम": "FCO",
    "fiumicino": "FCO",
    "milan": "MXP",
    "milán": "MXP",
    "malpensa": "MXP",
    "zurich": "ZRH",
    "zúrich": "ZRH",
    "geneva": "GVA",
    "ginebra": "GVA",
    "genf": "GVA",
    "vienna": "VIE",
    "viena": "VIE",
    "wien": "VIE",
    "berlin": "BER",
    "berlín": "BER",
    "munich": "MUC",
    "múnich": "MUC",
    "münchen": "MUC",
    "brussels": "BRU",
    "bruselas": "BRU",
    "lisbon": "LIS",
    "lisboa": "LIS",
    "dublin": "DUB",
    "dublín": "DUB",
    "moscow": "SVO",
    "moscú": "SVO",
    "москва": "SVO",
    "sheremetyevo": "SVO",
    "copenhagen": "CPH",
    "copenhague": "CPH",
    "stockholm": "ARN",
    "estocolmo": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "warsaw": "WAW",
    "varsovia": "WAW",
    "prague": "PRG",
    "praga": "PRG",
    "budapest": "BUD",
    "athens": "ATH",
    "atenas": "ATH",
    "istanbul": "IST",
    "estambul": "IST",
    "manchester": "MAN",
    "birmingham": "BHX",
    "edinburgh": "EDI",
    "edimburgo": "EDI",
    "glasgow": "GLA",
    # ===== NORTH AMERICA =====
    "new york": "JFK",
    "nueva york": "JFK",
    "न्यूयॉर्क": "JFK",
    "jfk": "JFK",
    "newark": "EWR",
    "los angeles": "LAX",
    "लॉस एंजिल्स": "LAX",
    "chicago": "ORD",
    "o'hare": "ORD",
    "san francisco": "SFO",
    "miami": "MIA",
    "washington": "IAD",
    "dulles": "IAD",
    "boston": "BOS",
    "seattle": "SEA",
    "denver": "DEN",
    "atlanta": "ATL",
    "dallas": "DFW",
    "houston": "IAH",
    "las vegas": "LAS",
    "phoenix": "PHX",
    "san diego": "SAN",
    "minneapolis": "MSP",
    "detroit": "DTW",
    "philadelphia": "PHL",
    "filadelfia": "PHL",
    "orlando": "MCO",
    "honolulu": "HNL",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "ottawa": "YOW",
    # ===== LATIN AMERICA =====
    "mexico city": "MEX",
    "ciudad de méxico": "MEX",
    "cdmx": "MEX",
    "cancun": "CUN",
    "cancún": "CUN",
    "guadalajara": "GDL",
    "monterrey": "MTY",
    "sao paulo": "GRU",
    "são paulo": "GRU",
    "san pablo": "GRU",
    "guarulhos": "GRU",
    "rio de janeiro": "GIG",
    "río de janeiro": "GIG",
    "galeão": "GIG",
    "buenos aires": "EZE",
    "ezeiza": "EZE",
    "santiago": "SCL",
    "lima": "LIM",
    "bogota": "BOG",
    "bogotá": "BOG",
    "medellin": "MDE",
    "medellín": "MDE",
    "panama city": "PTY",
    "ciudad de panamá": "PTY",
    "san jose": "SJO",
    "san josé": "SJO",
    "havana": "HAV",
    "la habana": "HAV",
    "caracas": "CCS",
    "quito": "UIO",
    # ===== OCEANIA =====
    "sydney": "SYD",
    "sídney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "auckland": "AKL",
    "wellington": "WLG",
    "christchurch": "CHC",
    "fiji": "NAN",
    "nadi": "NAN",
    # ===== AFRICA =====
    "johannesburg": "JNB",
    "cape town": "CPT",
    "ciudad del cabo": "CPT",
    "cairo": "CAI",
    "el cairo": "CAI",
    "القاهرة": "CAI",
    "nairobi": "NBO",
    "lagos": "LOS",
    "addis ababa": "ADD",
    "casablanca": "CMN",
    "marrakech": "RAK",
    "tunis": "TUN",
    "túnez": "TUN",
    "algiers": "ALG",
    "argel": "ALG",
    "mauritius": "MRU",
    "mauricio": "MRU",
    "seychelles": "SEZ",
    "dar es salaam": "DAR",
    "accra": "ACC",
}


class IATAService:
    """Hybrid service for IATA code lookups"""

    def __init__(self):
        self._amadeus_client: Any = None
        self._init_amadeus()

    def _init_amadeus(self):
        """Initialize Amadeus client for fallback lookups"""
        if settings.AMADEUS_API_KEY and settings.AMADEUS_API_SECRET:
            try:
                from amadeus import Client

                self._amadeus_client = Client(
                    client_id=settings.AMADEUS_API_KEY,
                    client_secret=settings.AMADEUS_API_SECRET,
                    hostname="test" if settings.AMADEUS_USE_TEST else "production",
                )
                logger.info("✅ Amadeus client ready for IATA lookups")
            except Exception as e:
                logger.warning(f"⚠️ Could not init Amadeus for IATA: {e}")

    def lookup(self, city_name: str) -> str | None:
        """
        Look up IATA code for a city.

        Strategy:
        1. Search local database (instant)
        2. If not found, try Amadeus API
        3. Cache results for future lookups

        Args:
            city_name: City name in any language

        Returns:
            3-letter IATA code or None
        """
        if not city_name:
            return None

        normalized = city_name.lower().strip()

        # Step 1: Search local database
        if normalized in IATA_DATABASE:
            code = IATA_DATABASE[normalized]
            logger.debug(f"✅ IATA found locally: {city_name} → {code}")
            return code

        # Step 2: If already an IATA code (3 letters), return it
        if len(normalized) == 3 and normalized.isalpha():
            return normalized.upper()

        # Step 3: Fallback to Amadeus API
        if self._amadeus_client:
            return self._lookup_amadeus(city_name)

        logger.warning(f"⚠️ IATA code not found for: {city_name}")
        return None

    def _lookup_amadeus(self, city_name: str) -> str | None:
        """Search Amadeus API as fallback"""
        if self._amadeus_client is None:
            return None
        try:
            response = self._amadeus_client.reference_data.locations.get(
                keyword=city_name,
                subType="AIRPORT,CITY",
            )
            if response.data:
                code: str = response.data[0]["iataCode"]
                logger.info(f"✅ IATA from Amadeus: {city_name} → {code}")
                # Cache for future lookups
                IATA_DATABASE[city_name.lower()] = code
                return code
        except Exception as e:
            logger.warning(f"⚠️ Amadeus IATA lookup failed: {e}")
        return None

    def get_city_name(self, iata_code: str) -> str | None:
        """Reverse lookup: get city name from IATA code"""
        iata_upper = iata_code.upper()
        for city, code in IATA_DATABASE.items():
            if code == iata_upper:
                return city.title()
        return None


# Singleton instance
_iata_service: IATAService | None = None


def get_iata_service() -> IATAService:
    """Get global IATAService instance"""
    global _iata_service
    if _iata_service is None:
        _iata_service = IATAService()
    return _iata_service

import requests
import pandas as pd
from datetime import datetime

class IMFClient:
    """
    Client for International Monetary Fund (IMF) JSON REST API.
    Focus: India (Area Code: 'IN')
    """
    
    BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
    
    def __init__(self):
        self.area_code = "IN"  # India
        
    def get_real_gdp_growth(self, start_year=2000, end_year=2024):
        """
        Fetches Real GDP Growth (NGDP_RPCH).
        """
        return self._fetch_series("NGDP_RPCH", start_year, end_year)

    def get_inflation(self, start_year=2000, end_year=2024):
        """
        Fetches Inflation, average consumer prices (PCPIPCH).
        """
        return self._fetch_series("PCPIPCH", start_year, end_year)

    def get_unemployment(self, start_year=2000, end_year=2024):
        """
        Fetches Unemployment rate (LUR).
        """
        return self._fetch_series("LUR", start_year, end_year)

    def _fetch_series(self, indicator, start_year, end_year):
        """
        Generic fetch method for IMF CompactData.
        Indicator: Code for the economic series.
        """
        # IMF API Structure for CompactData: /CompactData/{DatabaseID}/{Frequency}.{Area}.{Indicator}
        # WEO: World Economic Outlook database
        url = f"{self.BASE_URL}/CompactData/WEO/A.{self.area_code}.{indicator}"
        
        params = {
            "startPeriod": start_year,
            "endPeriod": end_year
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Navigate nested JSON response
            series_data = data['CompactData']['DataSet']['Series']['Obs']
            
            # Convert to standard format
            cleaned_data = []
            for entry in series_data:
                cleaned_data.append({
                    "year": int(entry['@TIME_PERIOD']),
                    "value": float(entry['@OBS_VALUE'])
                })
                
            return cleaned_data
            
        except Exception as e:
            print(f"Error fetching {indicator} from IMF: {e}")
            return []

if __name__ == "__main__":
    # Test
    client = IMFClient()
    print("India GDP Growth:", client.get_real_gdp_growth(2020, 2023))

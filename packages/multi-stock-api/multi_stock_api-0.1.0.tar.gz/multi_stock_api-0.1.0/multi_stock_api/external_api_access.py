from typing import List
from urllib.parse import urljoin
import requests
from .configurations import Configurations
from .models import MarketInfo


class ExternalApiAccess:
    @staticmethod
    def get_market_data():
        # Get all data from multiple API endpoints
        markets: List[MarketInfo] = Configurations().get_markets()
        for market in markets:
            # Prepare request
            body = requests.request(
                market.request_type, 
                urljoin(market.root_url, market.status_url),
                headers={ 'Content-type': market.content_type },
                data=market.request_info_params
            )

            # Handle response
            if body.status_code == 200:
                market.data = body.json()

        # Get only markets where data retrieved
        return list(filter(lambda api: api.data is not None and len(api.data) > 0, markets))
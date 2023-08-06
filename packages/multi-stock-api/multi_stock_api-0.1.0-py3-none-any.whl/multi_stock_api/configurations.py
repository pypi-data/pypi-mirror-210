from datetime import datetime
from typing import List

from .models import MarketInfo, Markets

class Configurations:
    _markets: List[MarketInfo] = []

    def __init__(self):
        self._markets.append(
            MarketInfo(
                content_type='application/x-www-form-urlencoded',
                field_name='SymbolDescription',
                field_average_percentage_change='AvgPerChange',
                field_latest_price='LastTradePrice',
                field_symbol='Symbol',
                name=Markets.SASE,
                request_type='POST',
                root_url='http://www.sase.ba',
                status_url='FeedServices/HandlerChart.ashx',
                type='json',
                request_info_params={ 
                    'id': 1, 
                    'type': 23, 
                    'dateFrom': datetime.today().strftime('%d.%m.%Y') 
                }
            )
        )

        self._markets.append(
            MarketInfo(
                field_name='Description',
                field_average_percentage_change='AvgPerChange',
                field_latest_price='AvgPrice',
                field_symbol='Code',
                name=Markets.BLBE,
                request_type='GET',
                root_url='https://www.blberza.com',
                status_url='services/defaultTicker.ashx',
                type='json',
                request_info_params={ 'langId': 1 }
            )
        )

    def get_markets(self) -> List[MarketInfo]:
        return self._markets
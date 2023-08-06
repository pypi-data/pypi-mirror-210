from .helpers import Helpers
from .models import MarketInfo, SymbolInfo

class Mappers:
    @staticmethod
    def map_api_results_to_symbol_info(market_info: MarketInfo, symbol: str) -> SymbolInfo:
        try:
            api_data = next(filter(lambda symbol_data: symbol_data[market_info.field_symbol] == symbol, market_info.data))
            result = SymbolInfo(
                market_name=market_info.name.value,
                average_percentage_change=Helpers.convert_to_percentage(str(api_data[market_info.field_average_percentage_change])),
                latest_price=Helpers.convert_to_money(api_data[market_info.field_latest_price]),
                symbol=symbol
            )
            return result
        except Exception as ex:
            print(f"Error parsing info - {ex}")
            return None
        
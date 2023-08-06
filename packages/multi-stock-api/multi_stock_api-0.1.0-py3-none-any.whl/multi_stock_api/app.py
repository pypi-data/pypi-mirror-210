from .external_api_access import ExternalApiAccess
from .mappers import Mappers
from .models import SymbolInfo


class StockInfo:
    def __init__(self):        
        self._markets_info = ExternalApiAccess.get_market_data()

    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        """
        Get single symbol info

        :param symbols: Ticker symbol
        """
        results = self.get_symbols_info([symbol])
        if results is not None and len(results) > 0:
            return results[0]
        return None

    def get_symbols_info(self, symbols):
        """
        Get multiple symbols info

        :param symbols: Ticker symbol list
        """
        results = []        
        
        if self._markets_info is not None:
            for symbol in symbols:
                for market_info in self._markets_info:
                    try:
                        result = Mappers.map_api_results_to_symbol_info(market_info, symbol)
                        if result is not None:
                            # Get first available symbol result in any market
                            results.append(result)
                            break
                    except Exception as ex:
                        print(f"Error retrieving market data - {ex}")
        
        return results

class Helpers:
    @staticmethod
    def convert_to_money(price):
        if isinstance(price, str):
            price = price.replace(',', '.')
        return float(price)
    
    @staticmethod
    def convert_to_percentage(value: str):
        if not value.endswith("%"):
            return f"{value}%"
        return value
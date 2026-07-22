from decimal import Decimal

def to_decimal(value):
    """
    İstənilən rəqəmi Decimal-ə çevirir.
    Float, int, Decimal, None və string dəyərləri işləyir.
    """
    if value is None:
        return Decimal('0.00')
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, Decimal):
        return value
    if isinstance(value, str):
        try:
            return Decimal(value)
        except:
            return Decimal('0.00')
    return Decimal(str(value))
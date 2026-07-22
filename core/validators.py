from decimal import Decimal
from rest_framework import serializers

def validate_quantity_for_unit(product, quantity):
    """
    product: Product instance
    quantity: str/int/float/Decimal
    Qaytarır: Decimal(quantity) — əgər uyğunsuzluq yoxdursa
    Xəta atır: unit='piece' olub, quantity kəsr olduqda
    """
    quantity = Decimal(str(quantity))
    if product.unit == "piece" and quantity != quantity.to_integral_value():
        raise serializers.ValidationError(
            f"'{product.name}' məhsulu ədədlə satılır, kəsr ədəd (məs. 1.5) daxil edilə bilməz."
        )
    return quantity
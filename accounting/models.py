from django.db import models
from core.models import Product, CustomUser

class PurchaseList(models.Model):
    currency = models.CharField(max_length=1, blank=True, null=True)
    class Meta:
        ordering = ("-id",)
        verbose_name = "Alış siyahısı"
        verbose_name_plural = "Alış siyahıları"

    def __str__(self):
        return str(self.id)

class Purchase(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('A', 'Anbarda')
    )
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="supplier_purchases")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="purchases")
    purchaselist = models.ForeignKey(PurchaseList, on_delete=models.CASCADE, related_name="purchaselist_purchases", blank=True, null=True)
    amount = models.FloatField("Miqdar", default=0)  # Float olaraq dəyişdirildi
    price = models.FloatField("Alış qiyməti", default=0)
    date = models.DateField("Alış tarixi", blank=True, null=True)
    status = models.CharField("Status", choices=STATUS, max_length=1, default='G')

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul alışı"
        verbose_name_plural = "Məhsul alışı"

    def __str__(self):
        return self.product.name
    
class Stock(models.Model):
    product = models.OneToOneField(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="stock")
    amount = models.FloatField(default=0)  # Float olaraq dəyişdirildi

    class Meta:
        ordering = ("-id",)
        verbose_name = "Stok"
        verbose_name_plural = "Anbar"

    def __str__(self):
        return self.product.name
    
class SaleList(models.Model):
    class Meta:
        ordering = ("-id",)
        verbose_name = "Satış siyahısı"
        verbose_name_plural = "Satış siyahıları"

    def __str__(self):
        return str(self.id)
    
    @property
    def total_amount(self):
        sales = self.salelist_sales.all()
        return sum([sale.amount * sale.price for sale in sales])

class Sale(models.Model):
    STATUS = (
        ('G', 'Gözləyir'),
        ('S', 'Satılıb')
    )
    seller = models.ForeignKey(CustomUser, verbose_name="Satıcı", on_delete=models.CASCADE, related_name="seller_sales", blank=True, null=True)
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_sales")
    salelist = models.ForeignKey(SaleList, verbose_name="Siyahı", on_delete=models.CASCADE, related_name="salelist_sales", blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_sales")
    amount = models.FloatField("Miqdar", default=0)  # Float olaraq dəyişdirildi
    datetime = models.DateTimeField("Tarix və vaxt", blank=True, null=True)
    price = models.FloatField("Satış qiyməti", blank=True, null=True)
    status = models.CharField("Status", choices=STATUS, max_length=1, default='G')

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul satışı"
        verbose_name_plural = "Məhsul satışı"

    def __str__(self):
        return self.product.name + " | " + self.customer.username
    
class Payment(models.Model):
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="payments")
    datetime = models.DateTimeField("Tarix və vaxt")
    amount = models.FloatField("Ödənilən məbləğ", default=0)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Ödəniş"
        verbose_name_plural = "Ödənişlər"

    def __str__(self):
        return self.customer.username
    
class ProductAction(models.Model):
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_actions")
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_product_actions", blank=True, null=True)
    date = models.DateField("Tarix")
    incoming_product_number = models.FloatField("Gələn məhsul sayı", blank=True, null=True)  # Float olaraq dəyişdirildi
    sold_product_number = models.FloatField("Satılan məhsul sayı", blank=True, null=True)  # Float olaraq dəyişdirildi
    remaining_product_number = models.FloatField("Qalan məhsul sayı", blank=True, null=True)  # Float olaraq dəyişdirildi
    return_product_number = models.FloatField("Qaytarılan məhsul sayı", blank=True, null=True)  # Float olaraq dəyişdirildi

    action = models.CharField("Hərəkət", max_length=250, default="-")

    class Meta:
        ordering = ("-id",)
        verbose_name = "Məhsul hərəkəti"
        verbose_name_plural = "Məhsul hərəkəti"

    def __str__(self):
        return self.product.name
    
class CustomerActionList(models.Model):
    class Meta:
        ordering = ("-id",)
        verbose_name = "Müştəri hərəkət siyahısı"
        verbose_name_plural = "Müştəri hərəkət siyahıları"

    def __str__(self):
        customer = self.c_customer_actions.first().customer.username if self.c_customer_actions.exists() else " "
        return str(self.id) + customer
    
class CustomerAction(models.Model):
    customeractionlist = models.ForeignKey(CustomerActionList, verbose_name="Siyahı", on_delete=models.CASCADE, related_name="c_customer_actions", blank=True, null=True)
    customer = models.ForeignKey(CustomUser, verbose_name="Müştəri", on_delete=models.CASCADE, related_name="customer_actions")
    product = models.ForeignKey(Product, verbose_name="Məhsul", on_delete=models.CASCADE, related_name="product_customer_actions", blank=True, null=True)
    date = models.DateField("Tarix")
    product_price = models.FloatField("Məhsul qiyməti", blank=True, null=True)
    payment_amount = models.FloatField("Ödənilən məbləğ", blank=True, null=True)
    total_amount = models.FloatField("Ümumi gəlir", blank=True, null=True)
    remaining_amount = models.FloatField("Qalan məbləğ", blank=True, null=True)
    return_amount = models.FloatField("Qaytarılan məbləğ", blank=True, null=True)

    action = models.CharField("Hərəkət", max_length=250, default="-")

    class Meta:
        ordering = ("-id",)
        verbose_name = "Müştəri hərəkəti"
        verbose_name_plural = "Müştəri hərəkəti"

    def __str__(self):
        return self.customer.username
    
class ReturnBack(models.Model):
    STATUS = (
        ('Y', 'Yararsız'),
        ('I', 'Işlək')
    )
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="returnbacks")
    date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    amount = models.FloatField()  # Float olaraq dəyişdirildi
    status = models.CharField(choices=STATUS, max_length=1, default="I")

    class Meta:
        verbose_name = "Geri qaytarma"
        verbose_name_plural = "Geri qaytarılan məhsullar"

    def __str__(self):
        return self.sale.product.name
    
class Expense(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.DateField()

    class Meta:
        verbose_name = "Xərc"
        verbose_name_plural = "Xərclər"

    def __str__(self):
        return self.name
    
class SupplierPayment(models.Model):
    CURRENCIES = (
        ('M', 'Manat'),
        ('D', 'Dollar'),
        ('R', 'Rubl')
    )
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="supplier_payments")
    amount = models.FloatField()
    currency = models.CharField(max_length=1, choices=CURRENCIES, default="M")
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = "Tədarükçü ödənişi"
        verbose_name_plural = "Tədarükçü ödənişləri"

    def __str__(self):
        return self.supplier.username
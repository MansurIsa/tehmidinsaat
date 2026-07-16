from rest_framework import serializers
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Product, ProductAbout, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem, WantedProduct
)
from accounting.models import ReturnBack
from django.contrib.auth.password_validation import validate_password

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "address", "password", "phone_number", "status", "is_staff", "is_superuser")

    def validate(self, data):
        validate_password(data["password"])
        return data
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username = validated_data["username"],
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            address = validated_data["address"],
            password = validated_data["password"],
            phone_number = validated_data["phone_number"],
            status = validated_data["status"],
            is_staff = validated_data["is_staff"],
            is_superuser = validated_data["is_superuser"]
        )
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ("password", "groups", "user_permissions")
    
class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    customer_debt_amount = serializers.SerializerMethodField()
    our_debt_amount = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ("id", "customer_debt_amount", "our_debt_amount")

    def get_total_amount(self, obj):
        total_amount = sum([sale.price * sale.amount for sale in obj.customer_sales.filter(status="S")])
        return total_amount
    
    def get_total_supplier_amount(self, obj):
        if obj.is_supplier:
            total_m_amount = sum([purchase.price * purchase.amount for purchase in obj.supplier_purchases.filter(status="A", purchaselist__currency="M")])
            total_d_amount = sum([purchase.price * purchase.amount for purchase in obj.supplier_purchases.filter(status="A", purchaselist__currency="D")])
            total_r_amount = sum([purchase.price * purchase.amount for purchase in obj.supplier_purchases.filter(status="A", purchaselist__currency="R")])
            return [total_m_amount, total_d_amount, total_r_amount]
        return None
    
    def get_total_paid_amount(self, obj):
        total_paid_amount = sum([payment.amount for payment in obj.payments.all()])
        return total_paid_amount
    
    def get_total_supplier_paid_amount(self, obj):
        if obj.is_supplier:
            total_supplier_m_paid_amount = sum([supplierpayment.amount for supplierpayment in obj.supplier_payments.filter(currency="M")])
            total_supplier_d_paid_amount = sum([supplierpayment.amount for supplierpayment in obj.supplier_payments.filter(currency="D")])
            total_supplier_r_paid_amount = sum([supplierpayment.amount for supplierpayment in obj.supplier_payments.filter(currency="R")])
            return [total_supplier_m_paid_amount, total_supplier_d_paid_amount, total_supplier_r_paid_amount]
    
    def calculate_customer_debt_amount(self, obj):
        return self.get_total_amount(obj) - self.get_total_paid_amount(obj)
    
    def get_customer_debt_amount(self, obj):
        if self.calculate_our_debt_amount(obj):
            total_customer_debt_amount = self.calculate_customer_debt_amount(obj) - self.calculate_our_debt_amount(obj)[0]
        else:
            total_customer_debt_amount = self.calculate_customer_debt_amount(obj)
        return total_customer_debt_amount if total_customer_debt_amount > 0 else 0
    
    def calculate_our_debt_amount(self, obj):
        if obj.is_supplier:
            results = []
            for i in range(3):
                results.append(self.get_total_supplier_amount(obj)[i] - self.get_total_supplier_paid_amount(obj)[i])
            return results
        return None
    
    def get_our_debt_amount(self, obj):
        if self.calculate_our_debt_amount(obj):
            total_our_debt_amount = self.calculate_our_debt_amount(obj)[0] - self.calculate_customer_debt_amount(obj)
            return [total_our_debt_amount if total_our_debt_amount > 0 else 0, self.calculate_our_debt_amount(obj)[1], self.calculate_our_debt_amount(obj)[2]]
        return None

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
    
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Article.objects.all(),
                fields=["product", "name"],
                message="Bu product üçün bu artikl artıq mövcuddur."
            )
        ]

class ProductAboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAbout
        fields = "__all__"

class ProductListSerializer(serializers.ModelSerializer):
    article_names = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", source="articles")
    measurement_unit_display = serializers.CharField(source="get_measurement_unit_display", read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', "degree", 'image', 'article_names', 'measurement_unit', 'measurement_unit_display', 'price', 'discount_price', 'amount')

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    articles = ArticleSerializer(many=True)
    product_abouts = ProductAboutSerializer(many=True)
    measurement_unit_display = serializers.CharField(source="get_measurement_unit_display", read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "degree", "image", "measurement_unit", "category")

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"

class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = "__all__"

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = "__all__"

class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = BasketItem
        fields = "__all__"

class BasketItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = "__all__"

class BasketCleanSerializer(serializers.Serializer):
    item_ids = serializers.ListField(
        child = serializers.IntegerField(), allow_empty=False
    )

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class ProductArticleSerializer(serializers.Serializer):
    article_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    articles = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    about_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    titles = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    contents = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class WantedProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantedProduct
        fields = "__all__"
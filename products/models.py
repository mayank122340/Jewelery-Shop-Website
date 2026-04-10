import random
import string
import uuid
import datetime
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone

# =============================================================================
# 1. CORE METAL & PRICING CONFIGURATION
# =============================================================================

class MetalRate(models.Model):
    """
    Global Metal Rates: Admin sets daily prices per gram here.
    The Pricing Engine uses these values to calculate real-time product prices.
    """
    METAL_CHOICES = (
        ('gold_24k', 'Gold 24K'),
        ('gold_22k', 'Gold 22K'),
        ('gold_18k', 'Gold 18K'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
    )
    metal_type = models.CharField(max_length=20, choices=METAL_CHOICES, unique=True)
    rate_per_gram = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_metal_type_display()}: ₹{self.rate_per_gram}"


# =============================================================================
# 2. USER AUTHENTICATION & PROFILES
# =============================================================================

class Profile(models.Model):
    """Extends the default Django User model to store additional customer info."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class OTPVerifier(models.Model):
    """Temporary storage for email verification codes with expiration logic."""
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Returns True if OTP is less than 2 minutes old."""
        now = timezone.now()
        diff = now - self.created_at
        return diff.total_seconds() <= 120


# =============================================================================
# 3. PRODUCT INVENTORY MANAGEMENT
# =============================================================================

class Product(models.Model):
    """
    The heart of the store. Includes automatic SKU generation, 
    automatic Weight calculation, and a Dynamic Pricing Engine.
    """
    METAL_CHOICES = [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum')]

    CATEGORY_CHOICES = [
        ('head', 'Head & Hair Jewellery'),
        ('ear', 'Ear Jewellery'),
        ('nose', 'Nose Jewellery'),
        ('neck', 'Neck & Chest Jewellery'),
        ('hand', 'Hand & Arm Jewellery'),
        ('waist', 'Waist Jewellery'),
        ('leg', 'Leg & Feet Jewellery'),
        ('men', 'Men’s Gold Jewellery'),
        ('traditional', 'Traditional Styles'),
    ]

    STATUS_CHOICES = [('available', 'In Stock'), ('sold', 'Sold Out')]

    # Identification & Basic Info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    sku = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    # Classification
    metal_type = models.CharField(max_length=20, choices=METAL_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=100)
    purity = models.CharField(max_length=50) # e.g., '18K', '22K'
    huid = models.CharField(max_length=20, blank=True, null=True)
    
    # Weight Metrics (Grams)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3)
    stone_weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    # Pricing Engine Configuration
    making_charges = models.DecimalField(max_digits=10, decimal_places=2)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.IntegerField(default=0) # Percentage
    
    # Media & Display
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def price_details(self):
        """
        PRICING ENGINE:
        Calculates Final Price based on current Metal Rates + Making Charges + 8% GST - Discounts.
        """
        # 1. Fetch current rate
        key = f"{self.metal_type.lower()}_{self.purity.lower().replace(' ', '')}" 
        if 'silver' in self.metal_type.lower(): key = 'silver'
        elif 'platinum' in self.metal_type.lower(): key = 'platinum'
            
        rate_obj = MetalRate.objects.filter(metal_type=key).first()
        rate = rate_obj.rate_per_gram if rate_obj else Decimal(0)

        # 2. Base Calculation
        metal_cost = self.net_weight * rate
        base_total = metal_cost + self.making_charges + self.other_charges
        
        # 3. Tax & Final Formatting
        gst_amount = base_total * Decimal('0.08')
        price_with_tax = base_total + gst_amount
        
        final_price = price_with_tax
        if self.discount > 0:
            final_price = price_with_tax - (price_with_tax * Decimal(self.discount) / 100)
        
        return {
            'rate_used': round(rate),
            'original_price': round(price_with_tax),
            'final_price': round(final_price),
            'has_discount': self.discount > 0,
            'discount_percent': self.discount
        }

    def save(self, *args, **kwargs):
        """Pre-save logic for auto-calculating weights, slugs, and SKUs."""
        # Auto Gross Weight
        self.gross_weight = Decimal(str(self.net_weight)) + Decimal(str(self.stone_weight))

        # Auto Slug
        if not self.slug:
            self.slug = slugify(self.name)
            if Product.objects.filter(slug=self.slug).exists():
                self.slug += "-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

        # Auto SKU (Format: MET-CAT-001)
        if not self.sku:
            prefix = f"{self.metal_type[:3].upper()}-{self.category[:3].upper()}"
            last_p = Product.objects.filter(sku__startswith=prefix).order_by('id').last()
            new_no = str(int(last_p.sku.split('-')[-1]) + 1).zfill(3) if last_p else "001"
            self.sku = f"{prefix}-{new_no}"

        super().save(*args, **kwargs)


# =============================================================================
# 4. SHOPPING SYSTEM (CART & WISHLIST)
# =============================================================================

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return sum(item.total_cost for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.price_details['final_price']


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)


# =============================================================================
# 5. ORDER MANAGEMENT & HISTORY
# =============================================================================

class Order(models.Model):
    """Stores final transaction details including snapshot of shipping address."""
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Placed', 'Order Placed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI / Netbanking'),
        ('CARD', 'Credit / Debit Card'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Shipping Snapshot (Important: Store here even if profile changes)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Order Meta
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD')
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{str(uuid.uuid4().int)[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} | {self.user.username}"


class OrderItem(models.Model):
    """
    Freeze Price Logic: Saves the exact price at the time of purchase 
    so future metal rate changes don't affect old orders.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
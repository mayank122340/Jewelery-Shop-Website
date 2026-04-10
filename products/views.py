# =============================================================================
# STANDARD LIBRARY IMPORTS
# =============================================================================
import json
import uuid
import random
from decimal import Decimal
from datetime import timedelta

# =============================================================================
# DJANGO CORE & UTILS IMPORTS
# =============================================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# Template & Email Utilities
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives

# =============================================================================
# AUTHENTICATION & PERMISSIONS
# =============================================================================
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

# =============================================================================
# PROJECT SPECIFIC IMPORTS (Models & Utils)
# =============================================================================
from .models import (
    Product, Profile, OTPVerifier, Wishlist, 
    Order, MetalRate, Cart, CartItem, OrderItem
)
from .utils import get_plot, get_comparison_plot

# PDF Generation Utility
from xhtml2pdf import pisa


# =============================================================================
# 1. SUPERUSER TOOLS (Price Control)
# =============================================================================

def set_rates(request):
    """
    Admin Tool: Updates daily rates for Gold, Silver, etc.
    ACCESS: Only Superuser (Owner)
    """
    # Security Check: jooo user superadmin noo hoy to anee dashboard home uprr mokliii dooo
    if not request.user.is_superuser:
        return redirect('dashboard_home')
    
    # 1. Ensure Default Rates Exist
    # joo database new bnaayo hoyy to auto ceation maate anee error thi bachvaa..
    defaults = ['gold_24k', 'gold_22k', 'gold_18k', 'silver', 'platinum']
    for metal in defaults:
        MetalRate.objects.get_or_create(metal_type=metal)

    # 2. Update Logic (Form Submission)
    if request.method == "POST":
        for metal in defaults:
            rate_val = request.POST.get(metal)
            
            # admin e rate aapyaa ho too update krvaa maateeeeeee
            if rate_val:
                rate_obj = MetalRate.objects.get(metal_type=metal)
                rate_obj.rate_per_gram = Decimal(rate_val)
                rate_obj.save()# aa linee thi database maa save thaaay
        
        # Save thyaa p6i paa6u e page ma laava maate
        return redirect('set_rates')

    # 3. Load Current Rates for Display
    rates = MetalRate.objects.all()
    return render(request, 'set_rates.html', {'rates': rates})


# =============================================================================
# 2. FRONTEND VIEWS (Customer Facing Pages)
# =============================================================================

def home_view(request):
    """
    Main Landing Page (Index):
    - Search & Filter handle karta hai.
    - Products ko Category-wise group karta hai (Sliders ke liye).
    """
    
    # --- STEP 1: BASE QUERY ---
    # Sirf 'available' products j btaava maate , Sold items customer nee nthi btaavana
    products_list = Product.objects.filter(status='available')

    # --- STEP 2: FETCH FILTER PARAMETERS ---
    # URL se data uthana (e.g., ?q=ring&metal=gold)
    query = request.GET.get('q')
    metal_type = request.GET.get('metal')
    min_weight = request.GET.get('min_weight')
    max_weight = request.GET.get('max_weight')

    # --- STEP 3: APPLY FILTERS (Smart Search) ---
    
    # A. Search Bar Logic (Name OR SKU OR Description)
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(description__icontains=query)# aama icontains case senstive bnava thyo 6
        )
    
    # B. Metal Filter (Gold/Silver)
    if metal_type:
        products_list = products_list.filter(metal_type=metal_type)

    # C. Weight Range Filter
    if min_weight:
        products_list = products_list.filter(net_weight__gte=min_weight)
    if max_weight:
        products_list = products_list.filter(net_weight__lte=max_weight)

    # --- STEP 4: DATA GROUPING FOR UI (Slider Logic) ---
    # Ye dictionary database keys ko 'Display Names' mein convert karti hai
    category_names = {
        'head': 'Head & Hair Jewellery',
        'ear': 'Elite Earring Collection',
        'nose': 'Nose Pins & Rings',
        'neck': 'Heritage Necklaces',
        'hand': 'Rings & Bangles',
        'men': "Men's Private Collection",
        'traditional': 'Traditional Styles'
    }
    
    grouped_data = {}

    # bdhaa product ne amni category id pramane group maa naakhooo
    for product in products_list.order_by('-id'):
        cat_id = str(product.category).lower().strip()
        
        # Agar ye category pehli baar aayi hai, to structure initialize karo
        if cat_id not in grouped_data:
            grouped_data[cat_id] = {
                'info': {
                    'id': cat_id,
                    'name': category_names.get(cat_id, cat_id.capitalize())
                },
                'products': []
            }
        
        # Product ko list mein add karo
        grouped_data[cat_id]['products'].append(product)

    # --- STEP 5: FINAL RENDER ---
    # 'grouped_data.values()' list bhej rahe hain jo template mein loop hogi
    return render(request, 'index.html', {
        'sections': list(grouped_data.values()),
        'search_query': query or '',
        'selected_metal': metal_type or ''
    })


def product_detail(request, slug):
    """
    Single Product Page:
    - Product ni bdhii details btaave .
    - 'Related Products' suggest kreee (Same category).
    """
    # 1. Main Product fetch karo (404 agar noo aave too)
    product = get_object_or_404(Product, slug=slug)
    
    # 2. Recommendation Logic
    # Same category ke items lo, par current product ko exclude (hata) do
    related_products = Product.objects.filter(
        category=product.category, 
        status='available'
    ).exclude(id=product.id)[:4] # Sirf top 4 dikhao

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

# =============================================================================
# 3. ADMIN DASHBOARD & MANAGEMENT (Staff Only)
# =============================================================================

# --- 1. DASHBOARD HOME (Overview) ---
@user_passes_test(lambda u: u.is_staff)
def dashboard_home(request):
    """
    Admin Dashboard Main View:
    - Lists all inventory items.
    - Handles 'Search' functionality.
    - Provides quick stats (Metal Counts) for top cards.
    """
    # 1. Search Logic: Agar user ne search bar mein kuch likha hai
    query = request.GET.get('search', '')
    if query:
        # Name ya SKU match hone par filter karo
        products = Product.objects.filter(name__icontains=query) | Product.objects.filter(sku__icontains=query)
    else:
        # Agar search nahi hai, toh saare products dikhao (Latest first)
        products = Product.objects.all().order_by('-id')

    # 2. Quick Stats: Sirf 'Available' stock ka count nikal rahe hain
    available_prods = Product.objects.filter(status='available')
    
    # Group by Metal Type (Gold, Silver, Platinum kitna hai)
    metal_counts = available_prods.values('metal_type').annotate(total=Count('id'))
    
    context = {
        'products': products,
        'metal_counts': metal_counts,
        'search_query': query,
    }
    return render(request, 'dashboard_home.html', context)


# --- 2. SALES ANALYTICS (Revenue & Comparison) ---
@user_passes_test(lambda u: u.is_staff)
def sales_analytics(request):
    """
    Advanced Analytics View:
    - Calculates Total Revenue & Orders.
    - Compares current week vs previous week performance.
    - Generates growth percentage.
    """
    # --- 1. BASIC STATS ---
    # Sirf unhi orders ka total lo jinka paisa aa gaya hai (payment_status=True)
    total_revenue = Order.objects.filter(payment_status=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.filter(payment_status=True).count()
    
    # --- 2. COMPARISON LOGIC (Week vs Week) ---
    # Default: Aaj se pichle 7 din vs uske pichle 7 din
    today = timezone.now().date()
    week1_start = today - timedelta(days=6)       # Current Week Start
    week2_start = week1_start - timedelta(days=7) # Last Week Start

    # Agar Admin ne custom date select ki hai toh wo use karo
    if request.GET.get('date1') and request.GET.get('date2'):
        week1_start = timezone.datetime.strptime(request.GET.get('date1'), '%Y-%m-%d').date()
        week2_start = timezone.datetime.strptime(request.GET.get('date2'), '%Y-%m-%d').date()

    # Helper Function: 7 din ka data nikalne ke liye
    def get_week_data(start_date):
        daily_data = []
        total = 0
        for i in range(7):
            day = start_date + timedelta(days=i)
            
            # Us din ki total sales (Sirf paid orders)
            day_sales = Order.objects.filter(
                order_date__date=day, payment_status=True
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            daily_data.append(day_sales)
            total += day_sales
        return daily_data, total

    # Dono weeks ka data fetch karo
    data1, total1 = get_week_data(week1_start) # Week 1 (Blue Line)
    data2, total2 = get_week_data(week2_start) # Week 2 (Grey Line)

    # Graph Generate karo (Utils function call)
    chart = get_comparison_plot(
        data1, data2, 
        label1=f"Week of {week1_start} (₹{total1})", 
        label2=f"Week of {week2_start} (₹{total2})"
    )

    # Growth Percentage Calculation
    growth = 0
    if total2 > 0:
        growth = ((total1 - total2) / total2) * 100
    elif total1 > 0:
        growth = 100

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'week1_total': total1,
        'week2_total': total2,
        'growth': round(growth, 1),
        'chart': chart,
        'default_date1': str(week1_start),
        'default_date2': str(week2_start),
    }
    return render(request, 'sales_analytics.html', context)


# --- 3. STOCK ANALYSIS (Category Breakdown) ---
def stock_analysis(request):
    """
    Inventory Reports:
    - Breaks down stock by Category (Pie Chart data).
    - Breaks down stock by Sub-Category (Detailed Table).
    """
    # Sabse Important: Sirf 'available' maal ka hisaab lagao
    available_prods = Product.objects.filter(status='available')
    
    # 1. Main Category Counts (e.g., Necklace: 50, Ring: 30)
    main_cat_analysis = available_prods.values('category').annotate(total=Count('id'))
    
    # 2. Sub-Category Counts (e.g., Choker: 20, Rani Haar: 30)
    sub_cat_analysis = available_prods.values('category', 'sub_category').annotate(total=Count('id')).order_by('category')
    
    context = {
        'main_cat_analysis': main_cat_analysis,
        'sub_cat_analysis': sub_cat_analysis,
    }
    return render(request, 'stock_analysis.html', context)


# =============================================================================
# 4. INVENTORY ACTIONS (Add Stock)
# =============================================================================

def add_stock(request):
    """
    Add New Product View:
    - Handles form submission.
    - Generates Automatic SKU (e.g., GOL-NEC-001).
    - Calculates Gross Weight automatically.
    """
    if request.method == "POST":
        # 1. Basic Data Fetching from Form
        name = request.POST.get('name')
        metal = request.POST.get('metal_type', 'gold')
        category = request.POST.get('category', 'other')
        purity = request.POST.get('purity')
        sub_category = request.POST.get('sub_category')
        huid = request.POST.get('huid')
        making_charges = request.POST.get('making_charges')
        image = request.FILES.get('image')
        description = request.POST.get('description', '')
        other_charges = request.POST.get('other_charges', 0)
        discount = request.POST.get('discount', 0)

        # 2. AUTOMATIC SKU GENERATION LOGIC
        # Format: [Metal 3 chars]-[Category 3 chars]-[Sequence Number]
        m_short = metal[:3].upper()
        c_short = category[:3].upper()
        prefix = f"{m_short}-{c_short}-"
        
        # Database check: Is prefix ka last product kaunsa tha?
        last_product = Product.objects.filter(sku__startswith=prefix).order_by('-id').first()
        
        if last_product and last_product.sku:
            try:
                # Last number nikalo aur +1 karo
                last_num = int(last_product.sku.split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        # Final SKU ban gaya (e.g., GOL-NEC-005)
        final_sku = f"{prefix}{str(new_num).zfill(3)}"

        # 3. Weights Calculation (Safety Check)
        try:
            nw = float(request.POST.get('net_weight', 0))
            sw = float(request.POST.get('other_weight', 0))
            gw = nw + sw # Gross Weight = Net + Stone
        except (ValueError, TypeError):
            nw, sw, gw = 0.0, 0.0, 0.0

        # 4. Create Product in Database
        try:
            Product.objects.create(
                status='available', # Default status
                sku=final_sku,
                name=name,
                metal_type=metal,
                category=category,
                sub_category=sub_category,
                purity=purity,
                huid=huid,
                gross_weight=gw,
                net_weight=nw,
                stone_weight=sw,
                making_charges=making_charges,
                image=image,
                other_charges=other_charges,
                discount=discount,
                description=description
            )
            return redirect('dashboard')
        
        except Exception as e:
            # Agar koi error aaye to print karo aur wahi page dikhao error ke saath
            print(f"Bhai Error aayi create karte waqt: {e}")
            return render(request, 'add_stock.html', {'error': f"Database Error: {e}"})

    return render(request, 'add_stock.html')


# =============================================================================
# 4. STOCK MONITORING & ALERTS
# =============================================================================

def stock_alerts_view(request):
    """
    Visual Inventory Health Monitor:
    - Calculates stock levels per category.
    - Assigns color codes based on quantity thresholds.
    """
    # 1. Fetch Data: Sirf 'available' items count karo
    available_prods = Product.objects.filter(status='available')
    cat_counts = available_prods.values('category').annotate(total=Count('id'))
    
    # 2. Logic for Color Coding
    alerts_data = []
    for cat in cat_counts:
        count = cat['total']
        
        # Threshold Logic:
        if count >= 20:
            color = "green"
            status = "Abundant"
        elif 15 <= count < 20:
            color = "blue"
            status = "Healthy"
        elif 5 <= count < 15:
            color = "yellow"
            status = "Moderate"
        else:
            color = "red"
            status = "Critical" # Less than 5 items
        
        alerts_data.append({
            'name': cat['category'],
            'count': count,
            'color': color,
            'status': status
        })

    return render(request, 'stock_alerts.html', {'alerts_data': alerts_data})


# =============================================================================
# 5. INVENTORY ACTIONS (Edit / Delete / Hide)
# =============================================================================

def edit_stock(request, pk):
    """
    Update Existing Product:
    - Fetches product by ID (pk).
    - Updates text fields.
    - Only updates the image if a new file is uploaded.
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == "POST":
        # Text Fields Update
        product.name = request.POST.get('name')
        product.metal_type = request.POST.get('metal_type')
        product.purity = request.POST.get('purity')
        product.category = request.POST.get('category')
        product.sub_category = request.POST.get('sub_category')
        
        # Weights & Pricing Update
        product.net_weight = request.POST.get('net_weight')
        product.stone_weight = request.POST.get('other_weight')
        product.making_charges = request.POST.get('making_charges')
        product.other_charges = request.POST.get('other_charges', 0)
        product.discount = request.POST.get('discount', 0)
        
        # Image Update (Conditional)
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
            
        product.save()
        return redirect('dashboard_home')
        
    return render(request, 'edit_stock.html', {'product': product})


def delete_stock(request, pk):
    """
    Hard Delete: Permanently removes the item from the database.
    Use carefully!
    """
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('dashboard_home')


def mark_as_sold(request, pk):
    """
    Soft Delete: Keeps the item in DB but hides it from the website.
    Updates status to 'sold'.
    """
    product = get_object_or_404(Product, pk=pk)
    product.status = 'sold'
    product.save()
    return redirect('dashboard_home')


# =============================================================================
# 6. AUTHENTICATION (Login & OTP System)
# =============================================================================

def auth_view(request):
    """
    Login View:
    - Handles User Sign In via Email & Password.
    - Redirects to Home page upon success.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using Email as Username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            # Login successful -> Redirect to Website Home
            return redirect('home') 
        else:
            # Login failed
            return render(request, 'auth/login.html', {'error': 'Invalid Email or Password'})
            
    return render(request, 'auth/login.html')


# --- AJAX View: Send OTP ---
def send_otp(request):
    """
    OTP Generation & Email Dispatch:
    1. Checks if email already exists (Duplicate Check).
    2. Generates 6-digit OTP.
    3. Sends Email via SMTP (with Console fallback).
    """
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required'})
    
    # 1. DUPLICATE USER CHECK
    if User.objects.filter(username=email).exists():
        return JsonResponse({
            'status': 'error', 
            'message': 'Account already exists! Please Sign In.'
        })

    # 2. GENERATE OTP
    otp = str(random.randint(100000, 999999))
    
    # Save to OTPVerifier Model
    OTPVerifier.objects.create(email=email, otp_code=otp)
    
    # 3. SEND EMAIL
    try:
        subject = 'Your Elite Verification Code'
        
        # Render Email Template
        html_content = render_to_string('emails/otp_email.html', {'otp': otp})
        text_content = strip_tags(html_content) # Plain text version
        
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        # Create Email Message
        msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        
        if settings.EMAIL_HOST_USER:
            msg.send()
        else:
            # Simulation Mode (If email settings aren't configured yet)
            print(f"📧 [ELITE SIMULATION] OTP for {email}: {otp}")
            
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        # Fallback mechanism
        print(f"Email Error: {e}")
        print(f"📧 [BACKUP OTP] OTP for {email}: {otp}") 
        return JsonResponse({'status': 'success', 'message': 'OTP sent (Check Console if email fails)'})


# --- AJAX View: Verify OTP ---
def verify_otp(request):
    """
    OTP Validation Logic:
    - Matches the latest OTP for the email.
    - Checks expiration (valid for 2 mins).
    """
    email = request.GET.get('email')
    otp = request.GET.get('otp')
    
    # Fetch Latest OTP
    verifier = OTPVerifier.objects.filter(email=email).last()
    
    if not verifier:
        return JsonResponse({'status': 'error', 'message': 'No OTP found'})
    
    # Check Code Match
    if verifier.otp_code == otp:
        # Check Time Expiration
        if verifier.is_valid():
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'OTP Expired'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
# =============================================================================
# 7. ACCOUNT REGISTRATION (Final Step)
# =============================================================================

def create_account(request):
    """
    Final Registration View:
    - Executed after OTP is verified.
    - Creates 'User' (Auth) and 'Profile' (Mobile) entries.
    - Auto-logs in the user after creation.
    """
    if request.method == "POST":
        # 1. Fetch Form Data
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Validation: Password Match
        if password != confirm_password:
            return render(request, 'auth/login.html', {'error': 'Passwords do not match'})

        # 3. Validation: Duplicate User Check
        if User.objects.filter(username=email).exists():
            return render(request, 'auth/login.html', {'error': 'User already exists'})

        # 4. Create User (Django Auth)
        user = User.objects.create_user(username=email, email=email, password=password)
        # Temporary name extraction (e.g., 'raj' from 'raj@gmail.com')
        user.first_name = email.split('@')[0] 
        user.save()

        # 5. Create Profile (Custom Data like Mobile)
        Profile.objects.create(user=user, mobile_number=mobile)

        # 6. Auto-Login & Redirect
        login(request, user)
        # Redirect to Website Home Page
        return redirect('home') 

    # If GET request, send back to login
    return redirect('login_page')


# =============================================================================
# 8. GENERAL DASHBOARD & ALERTS
# =============================================================================

def dashboard(request):
    """
    Basic Dashboard Redirect/View:
    - Ensures only logged-in users can access.
    - Loads latest products.
    """
    # Security Check
    if not request.user.is_authenticated:
        return redirect('login_page')
        
    # Fetch Data (Newest First)
    products = Product.objects.all().order_by('-id')
    
    # Render Dashboard Template
    return render(request, 'dashboard_home.html', {'products': products})


def stock_alerts(request):
    """Simple view to render the alerts page."""
    return render(request, 'stock_alerts.html')


def logout_view(request):
    """
    Logout Logic:
    - Clears user session.
    - Redirects to public home page.
    """
    logout(request) 
    return redirect('home') 


# =============================================================================
# 9. SUPERUSER MANAGEMENT (Create Sub-Admins)
# =============================================================================

@user_passes_test(lambda u: u.is_superuser)
def create_sub_admin(request):
    """
    Staff Creation Tool:
    - Allows the Owner (Superuser) to create Sub-Admins.
    - Sets 'is_staff = True' so they can access the Dashboard.
    """
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 🔥 SAFETY CHECK: Duplicate Email
        if User.objects.filter(username=email).exists():
            messages.error(request, f"Bhai, {email} se pehle se account bana hua hai!")
            return redirect('create_admin') # Reload page with error

        try:
            # 1. Create User Object
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            
            # 2. Grant Permissions (Crucial Step)
            user.is_staff = True  # Ye permission zaroori hai Dashboard access ke liye
            user.save()
            
            # 3. Success Feedback
            messages.success(request, f"Sub-Admin {name} ekdum perfect ban gaya!")
            return redirect('dashboard_home')
            
        except Exception as e:
            # Error Handling
            messages.error(request, f"Kuch gadbad hui: {e}")
            
    return render(request, 'admin_panel/create_admin.html')

# =============================================================================
# 10. CUSTOMER PROFILE MANAGEMENT
# =============================================================================

def user_profile(request):
    """
    User Dashboard:
    - Allows users to update their personal details (Address/Mobile).
    - Shows Order History and Wishlist.
    """
    # Security: Login zaroori hai
    if not request.user.is_authenticated:
        return redirect('login_page')
    
    # SAFE CHECK: Agar profile nahi hai, toh bana lo (Crash se bachne ke liye)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Data Fetching
    wishlist_items = Wishlist.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')

    if request.method == "POST":
        # 1. Update User First Name
        request.user.first_name = request.POST.get('name')
        request.user.save()
        
        # 2. Update Profile Details
        profile.mobile_number = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        
        # Safe Attribute Check (Agar future mein model change ho toh error na aaye)
        if hasattr(profile, 'city'): 
            profile.city = request.POST.get('city', '')
        if hasattr(profile, 'pincode'): 
            profile.pincode = request.POST.get('pincode', '')
        
        profile.save()
        return redirect('user_profile')

    return render(request, 'user_profile.html', {
        'profile': profile,
        'wishlist': wishlist_items,
        'orders': orders
    })


# =============================================================================
# 11. SHOPPING CART SYSTEM (Add / Update / Remove)
# =============================================================================

@login_required(login_url='login_page')
def add_to_cart(request, product_id):
    """Adds an item to the user's cart."""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get item or create if not exists
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Agar pehle se cart mein hai, to quantity badha do
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('view_cart')


@login_required(login_url='login_page')
def view_cart(request):
    """Displays the cart page."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required(login_url='login_page')
def update_cart_item(request, item_id):
    """Handles + and - buttons in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
        
        # Logic: Agar quantity 0 ho jaye, to item uda do
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
            
    return redirect('view_cart')


@login_required(login_url='login_page')
def remove_from_cart(request, item_id):
    """Removes an item completely from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')


# =============================================================================
# 12. CHECKOUT LOGIC (The Main Transaction Hub)
# =============================================================================

@login_required(login_url='login_page')
def checkout(request):
    """
    Final Checkout Process:
    1. Validates Cart.
    2. Creates Order Record.
    3. Moves items from Cart -> OrderItems.
    4. Marks products as 'Sold' (Hidden from website).
    5. Sends Confirmation Email.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Empty Cart Check
    if cart.items.count() == 0:
        return redirect('view_cart')
    
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        
        # --- STEP 1: Create Order Object ---
        order = Order(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address_line=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            total_amount=cart.total_price,
            payment_method=payment_method
        )

        # Payment Status Logic
        if payment_method == 'COD':
            order.payment_status = False
        else:
            order.payment_status = True # Online maana jayega (Logic expand kar sakte hain)
        
        order.save()

        # --- STEP 2: Move Items & Freeze Stock ---
        for item in cart.items.all():
            # A. Order Item create karna (History ke liye)
            OrderItem.objects.create(
                order=order, 
                product=item.product,
                quantity=item.quantity, 
                # Price Freeze: Taaki baad mein gold rate badhne se purana order change na ho
                price_at_purchase=item.product.price_details['final_price']
            )
            
            # B. 🔥 Product ko Website se hatana 
            # Hum delete nahi kar rahe, bas status 'sold' kar rahe hain
            product = item.product
            product.status = 'sold' 
            product.save()

        # --- STEP 3: Clear User Cart ---
        cart.items.all().delete()

        # --- STEP 4: Email Notification ---
        try:
            subject = f'Order Confirmed - #{order.order_id} | Rojesara Heritage'
            
            # Email Template Render
            html_content = render_to_string('emails/order_email.html', {'order': order})
            text_content = strip_tags(html_content) # Fallback
            
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [order.user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Error aaye toh server band na ho, bas print ho jaye
            print(f"Email Error: {e}") 

        # --- STEP 5: Final Response ---
        if payment_method == 'COD':
            return render(request, 'order_success.html', {'order': order})
        else:
            return render(request, 'payment_processing.html', {'order': order})

    return render(request, 'checkout.html', {'cart': cart, 'profile': profile})


# =============================================================================
# 13. ADMIN ORDER MANAGEMENT
# =============================================================================

@user_passes_test(lambda u: u.is_staff) 
def manage_orders(request):
    """Admin View: List all orders (Newest first)."""
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'admin_orders.html', {'orders': orders})


@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id):
    """Admin Action: Update status (Shipped, Delivered, Cancelled)."""
    if request.method == "POST":
        status = request.POST.get('status')
        order = get_object_or_404(Order, order_id=order_id)
        order.status = status
        order.save()
    return redirect('manage_orders')


@user_passes_test(lambda u: u.is_staff)
def get_order_details(request, order_id):
    """AJAX View: Fetches order details for the Admin Modal popup."""
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'admin_panel/order_modal_content.html', {'order': order})


# =============================================================================
# 14. POST-ORDER UTILITIES (Success & Invoice)
# =============================================================================

def order_success_view(request, order_id):
    """Simple Thank You page."""
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'order_success.html', {'order': order})


@login_required(login_url='login_page')
def download_invoice(request, order_id):
    """
    PDF Generator:
    - Uses xhtml2pdf to convert HTML Invoice -> PDF File.
    - Secure: Only the user who placed the order can download it.
    """
    order = get_object_or_404(Order, order_id=order_id, user=request.user) 
    
    template_path = 'invoice.html'
    context = {'order': order}
    response = HttpResponse(content_type='application/pdf')
    
    # Ye line browser ko batati hai ki ye file download karni hai
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
    return response
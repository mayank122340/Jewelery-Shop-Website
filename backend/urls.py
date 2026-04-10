from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from products import views  

urlpatterns = [
    # -------------------------------------------------------------------------
    # CORE SYSTEM & ADMIN RATED
    # -------------------------------------------------------------------------
    path('admin/', admin.site.urls),
    
    # -------------------------------------------------------------------------
    # CUSTOMER-FACING FRONTEND PAGES
    # -------------------------------------------------------------------------
    path('', views.home_view, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('account/profile/', views.user_profile, name='user_profile'),

    # -------------------------------------------------------------------------
    # SHOPPING SYSTEM: CART & CHECKOUT
    # -------------------------------------------------------------------------
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<str:order_id>/', views.order_success_view, name='order_success_page'),
    path('download-invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),

    # -------------------------------------------------------------------------
    # ADMIN DASHBOARD: ANALYTICS & STOCK MANAGEMENT
    # -------------------------------------------------------------------------
    path('dashboard/', views.dashboard_home, name='dashboard'), 
    path('dashboard/home/', views.dashboard_home, name='dashboard_home'), # Safety alias
    
    # Inventory Actions
    path('dashboard/add/', views.add_stock, name='add_stock'),
    path('dashboard/edit/<int:pk>/', views.edit_stock, name='edit_stock'),
    path('dashboard/delete/<int:pk>/', views.delete_stock, name='delete_stock'),
    path('dashboard/mark-sold/<int:pk>/', views.mark_as_sold, name='mark_as_sold'),

    # Data Analysis & Tools
    path('dashboard/analysis/', views.stock_analysis, name='stock_analysis'),
    path('dashboard/alerts/', views.stock_alerts_view, name='stock_alerts'),
    path('dashboard/analytics/', views.sales_analytics, name='sales_analytics'),
    path('dashboard/set-rates/', views.set_rates, name='set_rates'),
    
    # -------------------------------------------------------------------------
    # ORDER MANAGEMENT SYSTEM
    # -------------------------------------------------------------------------
    path('admin-panel/orders/', views.manage_orders, name='manage_orders'),
    path('admin-panel/orders/update/<str:order_id>/', views.update_order_status, name='update_order_status'),
    path('dashboard/get-order-details/<str:order_id>/', views.get_order_details, name='get_order_details'),

    # -------------------------------------------------------------------------
    # USER AUTHENTICATION & SECURITY
    # -------------------------------------------------------------------------
    path('auth/', views.auth_view, name='login_page'),
    path('auth/send-otp/', views.send_otp, name='send_otp'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('auth/create-account/', views.create_account, name='create_account'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('dashboard/create-admin/', views.create_sub_admin, name='create_admin'),
]

# -------------------------------------------------------------------------
# MEDIA FILES SERVING (DEBUG MODE ONLY)
# -------------------------------------------------------------------------
# Ye condition check karegi ki agar hum testing (DEBUG mode) mein hain
# toh uploaded photos (Media) ka rasta open rahega.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
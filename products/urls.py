from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from products import views  # Ensure views are imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Main Website ---
    path('', views.home_view, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # --- DASHBOARD URLs ---
    path('dashboard/', views.dashboard_home, name='dashboard'), 
    path('dashboard/home/', views.dashboard_home, name='dashboard_home'),
    
    path('dashboard/add/', views.add_stock, name='add_stock'),
    path('dashboard/edit/<int:pk>/', views.edit_stock, name='edit_stock'),
    path('dashboard/delete/<int:pk>/', views.delete_stock, name='delete_stock'),
    path('dashboard/mark-sold/<int:pk>/', views.mark_as_sold, name='mark_as_sold'),

    path('dashboard/analysis/', views.stock_analysis, name='stock_analysis'),
    path('dashboard/alerts/', views.stock_alerts_view, name='stock_alerts'),

    # CREATE ADMIN URL
    path('dashboard/create-admin/', views.create_sub_admin, name='create_admin'),
    path('dashboard/set-rates/', views.set_rates, name='set_rates'),
    path('admin-panel/orders/', views.manage_orders, name='manage_orders'),

    # --- AUTH URLs ---
    path('auth/', views.auth_view, name='login_page'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/send-otp/', views.send_otp, name='send_otp'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('auth/create-account/', views.create_account, name='create_account'),
   
   
   
]
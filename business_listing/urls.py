from django.urls import path, re_path
from django.shortcuts import redirect
from .views.add_business import add_business
from .views.edit_business import edit_business
from .views.edit_profile import edit_profile
from .views.delete_business import delete_business
from .views.business_categories import business_categories
from .views.businesses_by_category import businesses_by_category
from .views.businesses_by_country import businesses_by_country
from .views.country_list import country_list
from .views.businesses_by_city import businesses_by_postal_code
from .views.businesses_by_city_name import businesses_by_city_name
from .views.businesses_by_pobox import businesses_by_pobox
from .views.user_profile import user_profile
from .views.users_by_country import users_by_country
from .views.all_users import all_users
## removed invalid import from users_by_city (file deleted)
from .views.users_by_city_name import users_by_city_name
from .views.users_by_postal_code import users_by_postal_code
from .views.users_by_post_office_box import users_by_post_office_box
from .views.business_details import business_details
from .views.logout_view import logout_view
from .views.listed_businesses import listed_businesses
from .views.register import register
from .forms import EmailAuthenticationForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Legacy redirect for old city/<country_code>/<postal_code>/ URLs
    re_path(r'^city/(?P<country_code>[^/]+)/(?P<postal_code>[^/]+)/$', lambda request, country_code, postal_code: redirect('businesses_by_postal_code', country_code=country_code, postal_code=postal_code, permanent=True)),
    path('countries/', country_list, name='country_list'),
    path('add-business/', add_business, name='add_business'),
    path('business/<slug:slug>/edit/', edit_business, name='edit_business'),
    path('business/<slug:slug>/delete/', delete_business, name='delete_business'),
    path('categories/', business_categories, name='business_categories'),
    path('categories/<str:category>/', businesses_by_category, name='businesses_by_category'),
    path('country/<str:country_code>/', businesses_by_country, name='businesses_by_country'),
    path('postal_code/<str:country_code>/<str:postal_code>/', businesses_by_postal_code, name='businesses_by_postal_code'),
    path('city_name/<str:country_code>/<str:city>/', businesses_by_city_name, name='businesses_by_city_name'),
    path('pobox/<str:country_code>/<str:postal_code>/<int:post_office_box>/', businesses_by_pobox, name='businesses_by_pobox'),
    path('users/all/', all_users, name='all_users'),
    path('users/country/<str:country_code>/', users_by_country, name='users_by_country'),
    path('users/postal_code/<str:country_code>/<str:postal_code>/', users_by_postal_code, name='users_by_postal_code'),
    path('users/city_name/<str:country_code>/<str:city>/', users_by_city_name, name='users_by_city_name'),
    path('users/postal_code/<str:country_code>/<str:postal_code>/', users_by_postal_code, name='users_by_postal_code'),
    path('users/pobox/<str:country_code>/<str:postal_code>/<int:post_office_box>/', users_by_post_office_box, name='users_by_post_office_box'),
    path('user/<str:username>/', user_profile, name='user_profile'),
    path('user/<str:username>/edit/', edit_profile, name='edit_profile'),
    path('business/<slug:slug>/', business_details, name='business_details'),
    path('logout/', logout_view, name='logout'),
    path('', listed_businesses, name='listed_businesses'),
    path('login/', auth_views.LoginView.as_view(template_name='business_listing/login.html', authentication_form=EmailAuthenticationForm), name='login'),
    path('register/', register, name='register'),
]
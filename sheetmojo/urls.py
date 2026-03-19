from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
import importlib.util
from django.urls import reverse_lazy
from home import views as home_views

urlpatterns = [
    path('', home_views.index, name='home'),
    path('home/', include('home.urls')),
    path('login', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path(
        'password-reset',
        auth_views.PasswordResetView.as_view(
            template_name='auth/password_reset.html',
            success_url=reverse_lazy('password_reset_done'),
            email_template_name='auth/password_reset_email.txt',
        ),
        name='password_reset',
    ),
    path(
        'password-reset-done',
        auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete',
        auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('register', home_views.register, name='register'),
    path('profile', home_views.profile, name='profile'),
    path('dashboard', home_views.dashboard, name='dashboard'),
    path('calculators', home_views.calculator_directory, name='calculator-directory'),
    path('categories', home_views.categories, name='categories'),
    path('tags', home_views.tags, name='tags'),
    path('add', home_views.add_calculator, name='add-calculator'),
    path('admin/calculators', home_views.calculator_list, name='calculator-list'),
    path('calculator/<int:pk>/update', home_views.update_calculator, name='update-calculator'),
    path('calculator/<int:pk>/delete', home_views.delete_calculator, name='delete-calculator'),
    path('admin/users', home_views.admin_users, name='admin-users'),
    path('terms-of-use', home_views.terms_of_use, name='terms-of-use'),
    path('privacy-policy', home_views.privacy_policy, name='privacy-policy'),
    path('volume/', include('volume.urls')),
    path('area/', include('area.urls')),
    path('calculus/', include('calculus.urls')),
    path('statistics/', include('statistics_app.urls')),
    path('matrix/', include('matrix.urls')),
    path('algebra/', include('algebra.urls')),
    path('geometry/', include('geometry.urls')),
    path('trigonometry/', include('trigonometry.urls')),
    path('physics/', include('physics.urls')),
    path('chemistry/', include('chemistry.urls')),
    path('geography/', include('geography.urls')),
    path('business/', include('business.urls')),
    path('agriculture/', include('agriculture.urls')),
    path('biology/', include('biology.urls')),
    path('engineering/', include('engineering.urls')),
    path('computing/', include('computing.urls')),
    path('cosmology/', include('cosmology.urls')),
    path('mathematics/', include('mathematics.urls')),
    path('mechanics/', include('mechanics.urls')),
    path('aviation/', include('aviation.urls')),
    path('electronics/', include('electronics.urls')),
    path('telecomunications/', include('telecomunications.urls')),
    path('dj-admin/', admin.site.urls),
]

if importlib.util.find_spec("algos") is not None:
    urlpatterns.insert(0, path('', include('algos.urls')))

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django_countries import countries
from ..models import UserProfile

@login_required
def edit_profile(request, username):
    User = get_user_model()
    if request.user.username != username:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('user_profile', username=request.user.username)
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    if request.method == 'POST':
        profile.about_me = request.POST.get('about_me', '').strip()
        profile.country = request.POST.get('country', '').strip().upper() or None
        profile.city = request.POST.get('city', '').strip()
        profile.postal_code = request.POST.get('postal_code', '').strip()
        pobox = request.POST.get('post_office_box', '')
        try:
            profile.post_office_box = int(pobox) if pobox else None
        except (ValueError, TypeError):
            messages.error(request, 'Post office box must be a whole number.')
            profile.post_office_box = None
            context = {
                'profile': profile,
                'profile_user': profile_user,
                'country_choices': list(countries),
            }
            return render(request, 'business_listing/edit_profile.html', context)
        profile.save()
        messages.success(request, 'Your profile has been updated.')
        return redirect('user_profile', username=username)
    context = {
        'profile': profile,
        'profile_user': profile_user,
        'country_choices': list(countries),
    }
    return render(request, 'business_listing/edit_profile.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from ..models import UserProfile, BusinessDetails

def user_profile(request, username):
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    # Get profile (create if it doesn't exist - optional)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    businesses = BusinessDetails.objects.filter(
        created_by=profile_user
    ).order_by('-created_on')
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'businesses': businesses,
        'business_count': businesses.count(),
    }
    return render(request, 'business_listing/user_profile.html', context)
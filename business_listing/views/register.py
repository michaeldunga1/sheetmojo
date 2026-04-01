from ..forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, render

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to SheetMojo. Your account has been created successfully.')
            return redirect('home')
        messages.error(request, 'Please correct the highlighted fields and try again.')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}
    return render(request, 'business_listing/register.html', context)

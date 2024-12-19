from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def register(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)  # Create a profile for the new user
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """
    Display and update user profile.
    """
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile was updated successfully!")
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {'profile_form': profile_form})

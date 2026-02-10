from django.shortcuts import redirect
from django.contrib import messages

def email_verified_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_verified:
            messages.error(request, '❌ ابتدا ایمیل خود را تایید کنید')
            return redirect('jobs:home')

        return view_func(request, *args, **kwargs)
    return wrapper

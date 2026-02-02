from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ShortenedURL
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils.timezone import now
from .utils import generate_short_key, generate_qr_code
from django.urls import reverse 
import re

# Create your views here.
@login_required
def dashboard(request):
    urls = ShortenedURL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shortener/dashboard.html', {'urls': urls})

@login_required
def create_short_url(request):
    short_url = None
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        expires_at_raw = request.POST.get('expires_at')
        custom_key = request.POST.get('custom_key')
        if custom_key:
            if not re.match(r'^[a-zA-Z0-9_-]+$', custom_key):
                return render(request, "shortener/create_short_url.html", {
                    "error": "Custom URL can only contain letters, numbers, _ and -"
                })
            short_key = custom_key
        else:
            short_key = generate_short_key()


        if ShortenedURL.objects.filter(short_key=short_key).exists():
            error = "Custom key already in use. Please choose another one."
            return render(request, 'shortener/create_short_url.html', {'error': error})
        
        expires_at = None

        if expires_at_raw:
           expires_at = timezone.make_aware(
                 parse_datetime(expires_at_raw)
            )

        short = ShortenedURL.objects.create(
            user=request.user,
            original_url=original_url,
            short_key=short_key,
            expires_at=expires_at
        )
        
        short_url = request.build_absolute_uri(reverse('redirect', args=[short.short_key]))

        short.qr_code.save(
            f"{short.short_key}.png",
            generate_qr_code(short_url),
            save=True
        )
    return render(request, 'shortener/create_short_url.html', {'short_url': short_url})

def redirect_short_url(request, short_key):
    url = get_object_or_404(ShortenedURL, short_key=short_key)
    if url.is_expired():
        return render(request, 'shortener/expired.html', status=410)
    url.clicks += 1
    url.save()
    return HttpResponseRedirect(url.original_url)

@login_required
def delete_short_url(request, pk):
    url = get_object_or_404(ShortenedURL, pk=pk, user=request.user)
    url.delete()
    return redirect('dashboard')

@login_required
def edit_short_url(request, pk):
    url = get_object_or_404(ShortenedURL, pk=pk, user=request.user)
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        custom_key = request.POST.get('custom_key')
        expires_at_raw = request.POST.get('expires_at')

        if custom_key:
            if not re.match(r'^[a-zA-Z0-9_-]+$', custom_key):
                return render(request, "shortener/edit_short_url.html", {
                    "url": url,
                    "error": "Custom URL can only contain letters, numbers, _ and -"
                })
            if ShortenedURL.objects.filter(short_key=custom_key).exclude(pk=pk).exists():
                error = "Custom key already in use. Please choose another one."
                return render(request, 'shortener/edit_short_url.html', {'url': url, 'error': error})
            url.short_key = custom_key

        url.original_url = original_url
        if expires_at_raw:
            url.expires_at = timezone.make_aware(
                parse_datetime(expires_at_raw)
            )
        else:
            url.expires_at = None
        url.save()
        return redirect('dashboard')
    return render(request, 'shortener/edit_short_url.html', {'url': url})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
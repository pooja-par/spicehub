from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest
from .forms import ContactForm

def contact_view(request: HttpRequest):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.ip_address = request.META.get('REMOTE_ADDR')
            contact.save()
            messages.success(request, 'Thank you! Your message has been submitted.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})
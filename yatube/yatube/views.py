from django.shortcuts import render

from .forms import ContactForm


def user_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            return render(request, 'thank_you.html')

        return render(request, 'contact.html', {'form': form})

    form = ContactForm()
    return render(request, 'contact.html', {'form': form})

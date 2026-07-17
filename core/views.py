from django.shortcuts import render


def public_home(request):
    return render(request, 'common/home.html')

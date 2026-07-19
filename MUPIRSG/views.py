from django.shortcuts import render
from HomePage.models import HomePage
from activities.models import Activity,ActivityPage 
from aboutpage.models import AboutPage
from bookpage.models import PdfBook
import json


def Home(request):
    homepage = HomePage.objects.first()   # Get the first record
    activities = Activity.objects.filter(is_active=True)[:3]

    context = {
        "homepage": homepage,
        "activities": activities,
    }

    return render(request, "index.html", context)
def about(request):
    about = AboutPage.objects.first()
    return render(request, "about.html", {"about": about})

def activities(request):
    page = ActivityPage.objects.first()

    activities = Activity.objects.filter(
        is_active=True
    ).order_by("order")

    return render(
        request,
        "activities.html",
        {
            "page": page,
            "activities": activities,
        },
    )
def current_council(request):
    return render(request,'current-crew-council.html')
def crew_council(request):
    return render(request,'crew-council.html')
def crew_img(request):
    return render(request,'crew_image.html')
def event(request):
    return render(request,'events.html')
def hiking_img(request):
    return render(request,'hinikg_img.html')
def mut(request):
    return render(request,'mut.html')
def dikkha_img(request):
    return render(request,'dikkha.html')
def contact(request):
    return render(request,'contact.html')
def book(request):
    books = PdfBook.objects.filter(is_active=True)

    pdf_data = [
        {"alt": b.title, "url": b.file.url}
        for b in books
    ]

    context = {
        "pdf_data_json": json.dumps(pdf_data),
    }
    return render(request, "book.html", context)
from django.shortcuts import render
from HomePage.models import HomePage
from activities.models import Activity, ActivityPage 
from aboutpage.models import AboutPage
from bookpage.models import PdfBook
from crewgallery.models import CrewImage, CrewHero
from dikkhagallery.models import DikkhaHero, DikkhaImage
from hikinggallery.models import HikingHero, HikingImage
from mutgallery.models import MutHero, MutImage
from eventgallery.models import EventHero, EventImage
from contactpage.models import ContactPage, SocialLink, FAQItem
import json
from councilpage.models import Council



def Home(request):
    homepage = HomePage.objects.first()
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
    return render(request, 'current-crew-council.html')


def crew_council(request):
    councils = Council.objects.filter(is_active=True).prefetch_related("members")

    new_council_data = []
    for council in councils:
        members = council.members.all()

        senior = members.filter(role="senior_rover").first()
        rover_mates = members.filter(role="rover_mate")
        assistant_mates = members.filter(role="assistant_rover_mate")

        new_council_data.append({
            "id": f"db-{council.id}",  # prefix to avoid clashing with JSON ids
            "name": council.name,
            "year": council.year,
            "seniorRover": {
                "name": senior.name,
                "department": senior.department,
                "subgroup": senior.subgroup,
                "image": senior.image.url if senior and senior.image else "",
            } if senior else {},
            "roverMates": [
                {
                    "name": m.name,
                    "department": m.department,
                    "subgroup": m.subgroup,
                    "image": m.image.url if m.image else "",
                } for m in rover_mates
            ],
            "assistantRoverMates": [
                {
                    "name": m.name,
                    "department": m.department,
                    "subgroup": m.subgroup,
                    "image": m.image.url if m.image else "",
                } for m in assistant_mates
            ],
        })

    context = {
        "new_council_json": json.dumps(new_council_data),
    }
    return render(request, "crew-council.html", context)

def crew_img(request):
    hero = CrewHero.objects.first()
    images = CrewImage.objects.filter(is_active=True)

    new_images_data = [
        {"url": img.image.url, "alt": img.title or ""}
        for img in images
    ]

    context = {
        "hero": hero,
        "new_images_json": json.dumps(new_images_data),
    }
    return render(request, "crew_image.html", context)


def event(request):
    hero = EventHero.objects.first()
    images = EventImage.objects.filter(is_active=True)

    new_images_data = [
        {"url": img.image.url, "alt": img.title or ""}
        for img in images
    ]

    context = {
        "hero": hero,
        "new_images_json": json.dumps(new_images_data),
    }
    return render(request, "events.html", context)

def hiking_img(request):
    hero = HikingHero.objects.first()
    images = HikingImage.objects.filter(is_active=True)

    new_images_data = [
        {"url": img.image.url, "alt": img.title or ""}
        for img in images
    ]

    context = {
        "hero": hero,
        "new_images_json": json.dumps(new_images_data),
    }
    return render(request, "hinikg_img.html", context)

def mut(request):
    hero = MutHero.objects.first()
    images = MutImage.objects.filter(is_active=True)

    new_images_data = [
        {"url": img.image.url, "alt": img.title or ""}
        for img in images
    ]

    context = {
        "hero": hero,
        "new_images_json": json.dumps(new_images_data),
    }
    return render(request, "mut.html", context)

def dikkha_img(request):
    hero = DikkhaHero.objects.first()
    images = DikkhaImage.objects.filter(is_active=True)

    new_images_data = [
        {"url": img.image.url, "alt": img.title or ""}
        for img in images
    ]

    context = {
        "hero": hero,
        "new_images_json": json.dumps(new_images_data),
    }
    return render(request, "dikkha.html", context)


def contact(request):
    contact_info = ContactPage.objects.first()
    social_links = SocialLink.objects.filter(is_active=True)
    faqs = FAQItem.objects.filter(is_active=True)

    context = {
        "contact_info": contact_info,
        "social_links": social_links,
        "faqs": faqs,
    }
    return render(request, "contact.html", context)

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
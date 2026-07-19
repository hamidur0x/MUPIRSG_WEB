"""
URL configuration for MUPIRSG project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MUPIRSG import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path( '', views.Home, name='HomePage'),
    path('about/', views.about, name='AboutPage'),
    path('activities/', views.activities,name='ActivitiesPAge'),
    path('current_council/', views.current_council, name='CurrentCouncilPage'),
    path('crew_council/', views.crew_council, name='CrewCouncilPage'),
    path('crew_img/',views.crew_img,name='CrewImgPage'),
    path('event/',views.event,name='EventPage'),
    path('hiking_img/',views.hiking_img,name='HikingImgPage'),
    path('mut/',views.mut,name='MutPage'),
    path('dikkha_img/',views.dikkha_img, name='DikkhaImgPage'),
    path('contact/',views.contact,name='ContactPage'),
    path('books/',views.book,name='BookPage')
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
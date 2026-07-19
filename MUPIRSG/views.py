from django.shortcuts import render 

def home(request):
    return render( request ,'index.html')
def about(request):
    return render(request, 'about.html')
def activities(request):
    return render(request,'activities.html' )
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
    return render(request,'book.html')
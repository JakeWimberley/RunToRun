from django.shortcuts import render
from django.db.models import Q
from .models import Event, Pin

# Create your views here.

def home(request):
	timelineEvents = Event.objects.filter(Q(owner=request.user)|Q(isPublic=True))
	pinned = Pin.objects.filter(owner=request.user)
	return render(request, 'tracker/home.html', { \
    'timelineEvents': timelineEvents, \
    'pinned': pinned, \
  })

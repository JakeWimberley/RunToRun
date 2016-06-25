from django.shortcuts import render
from django.db.models import Q
from .models import Event

# Create your views here.

def home(request):
	events = Event.objects.filter(Q(owner=request.user)|Q(isPublic=True))
	return render(request, 'tracker/home.html', {'events': events})

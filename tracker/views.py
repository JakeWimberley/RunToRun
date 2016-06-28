"""
    Copyright 2016 Jake Wimberley.

    This file is part of RunToRun.

    RunToRun is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RunToRun is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with RunToRun.  If not, see <http://www.gnu.org/licenses/>.
"""
from django.shortcuts import render
from django.db.models import Q
from .models import Discussion, Event, Pin
from .forms import DiscussionForm

# Create your views here.

def home(request):
	timelineEvents = Event.objects.filter(Q(owner=request.user)|Q(isPublic=True))
	pinned = Pin.objects.filter(owner=request.user)
	if request.method == 'POST':
		newDiscussion = DiscussionForm(request.POST,eventList=pinned)
		if newDiscussion.is_valid():
			_valid = newDiscussion.cleaned_data['_valid']
			_text = newDiscussion.cleaned_data['_text']
			_event = newDiscussion.cleaned_data['_event']
			discoObj = Discussion(author=request.user,validDate=_valid,text=_text)
			discoObj.save()
			return HttpResponseRedirect('/')
	else:
		newDiscussion = DiscussionForm(eventChoices=pinned)
	return render(request, 'tracker/home.html', { \
    'timelineEvents': timelineEvents, \
    'pinned': pinned, \
    'newDiscussion': newDiscussion
  })

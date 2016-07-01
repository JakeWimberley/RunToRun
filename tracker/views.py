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
from django.http import HttpResponseRedirect, HttpResponse
from .models import Discussion, Event, Pin
from .forms import DiscussionForm
import datetime
import pytz
import re

# Create your views here.

def home(request):
	timelineEvents = Event.objects.filter(Q(owner=request.user)|Q(isPublic=True))
	pinned = Pin.objects.filter(owner=request.user)
	if request.method == 'POST':
		newDiscussion = DiscussionForm(request.POST,eventChoices=pinned)
		if newDiscussion.is_valid():
			_validDate = newDiscussion.cleaned_data['_validDate']
			_validTime = newDiscussion.cleaned_data['_validTime']
			_text = newDiscussion.cleaned_data['_text']
			_event = newDiscussion.cleaned_data['_event']
			_valid = datetime.datetime.combine(_validDate,_validTime)
			_valid = _valid.replace(tzinfo=pytz.UTC)
			listStart = _valid.strftime('%Y%m%d_0000')
			listEnd = _valid.strftime('%Y%m%d_2359')
			discoObj = Discussion(author=request.user,validDate=_valid,text=_text)
			discoObj.save()
			return HttpResponseRedirect('/discussions/{0:s}/{1:s}'.format(listStart,listEnd))
	else:
		newDiscussion = DiscussionForm(eventChoices=pinned)
	return render(request, 'tracker/home.html', { \
    'timelineEvents': timelineEvents, \
    'pinned': pinned, \
    'newDiscussion': newDiscussion
  })

def discussionRange(request, _timeFrom, _timeTo):
	timePattern = re.compile(r'(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)')
	tF = timePattern.match(_timeFrom)
	tT = timePattern.match(_timeTo)
	if tF and tT:
		timeFrom = datetime.datetime(int(tF.group(1),10),int(tF.group(2),10),int(tF.group(3),10),int(tF.group(4),10),int(tF.group(5),10),second=0,tzinfo=pytz.UTC)
		timeTo = datetime.datetime(int(tT.group(1),10),int(tT.group(2),10),int(tT.group(3),10),int(tT.group(4),10),int(tT.group(5),10),second=59,tzinfo=pytz.UTC)
#timeTo = datetime.datetime(tT.match(1),tT.match(2),tT.match(3),tT.match(4),tT.match(5),tzinfo=pytz.UTC)
		discos = Discussion.objects.filter(validDate__gte=timeFrom,validDate__lte=timeTo)
	return render(request, 'tracker/discussionRange.html', { \
    'discussions': discos, \
    'timeFrom': timeFrom, \
		'timeTo': timeTo
  })

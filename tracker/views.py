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
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponse
from .models import Discussion, Event, Pin
from .forms import DiscussionForm, DiscussionFormTextOnly, EventForm
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
# TODO use _event
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
		vDates = [v['validDate'] for v in Discussion.objects.filter(validDate__gte=timeFrom,validDate__lte=timeTo).order_by('validDate').values('validDate').annotate(Count('validDate',distinct=True))]
		discos = {}
		for vDate in vDates:
			discos[vDate] = Discussion.objects.filter(validDate=vDate).order_by('-createdDate')
	return render(request, 'tracker/discussionRange.html', { \
    'validDates': vDates, \
    'discussions': discos, \
    'timeFrom': timeFrom, \
    'timeTo': timeTo
  })

def concurrentDiscussion(request, _id):
	"A standalone discussion form with the validDate and event defined by an existing discussion."
	parent = Discussion.objects.get(id=_id)
	_valid = parent.validDate
	if request.method == 'POST':
		newDiscussion = DiscussionFormTextOnly(request.POST)
		if newDiscussion.is_valid():
			_text = newDiscussion.cleaned_data['_text']
			listStart = _valid.strftime('%Y%m%d_0000')
			listEnd = _valid.strftime('%Y%m%d_2359')
# TODO use _event
			discoObj = Discussion(author=request.user,validDate=_valid,text=_text)
			discoObj.save()
			return HttpResponseRedirect('/discussions/{0:s}/{1:s}'.format(listStart,listEnd))
	else:
		textBox = DiscussionFormTextOnly()
	return render(request, 'tracker/concurrentDiscussion.html', {
		'id': _id,
		'validTime': _valid,
		'discussionTextBox': textBox,
	})

def allDiscussions(request):
	vTimes = [x['validDate'] for x in Discussion.objects.all().order_by('validDate').values('validDate').annotate(Count('validDate',distinct=True))]
	discos = {}
	for vTime in vTimes:
		discos.append(Discussion.objects.filter(validDate=vTime).order_by('-createdDate'))
	timeFrom = 'the beginning of time'
	timeTo = 'the end of time'
	return render(request, 'tracker/discussionRange.html', { \
    'validDates': vTimes, \
    'discussions': discos, \
    'timeFrom': timeFrom, \
		'timeTo': timeTo
  })

def newEvent(request):
	if request.method == 'POST':
		newEvent = EventForm(request.POST)
		if newEvent.is_valid():
			_title = newEvent.cleaned_data['_title']
			_startDate = newEvent.cleaned_data['_startDate']
			_startTime = newEvent.cleaned_data['_startTime']
			_endDate = newEvent.cleaned_data['_endDate']
			_endTime = newEvent.cleaned_data['_endTime']
			_isPublic = newEvent.cleaned_data['_isPublic']
			_isPermanent = newEvent.cleaned_data['_isPermanent']
			_start = datetime.datetime.combine(_startDate,_startTime).replace(tzinfo=pytz.UTC)
			_end = datetime.datetime.combine(_endDate,_endTime).replace(tzinfo=pytz.UTC)
			obj = Event(owner=request.user,title=_title,startDate=_start,endDate=_end,isPublic=_isPublic,isPermanent=_isPermanent)
			obj.save()
			_isPinned = newEvent.cleaned_data['_isPinned']
			if _isPinned:
				pin = Pin(owner=request.user,event=obj)
				pin.save()
			return HttpResponseRedirect('/')
#return HttpResponseRedirect('/events/{0:s}/'.format(obj.id))
	else:
		newEvent = EventForm()
	return render(request, 'tracker/newEvent.html', { \
    'newEventForm': newEvent \
  })

def singleEvent(request, _id):
	thisEvent = Event.objects.filter(id=_id)
	thisEvent = thisEvent[0]
	eventDiscussions = thisEvent.discussions.all()
	vDates = [x['validDate'] for x in eventDiscussions.order_by('validDate').values('validDate').annotate(Count('validDate',distinct=True))]
	discos = {}
	for vDate in vDates:
		discos[vDate] = eventDiscussions.filter(validDate=vDate).order_by('-createdDate')
	return render(request, 'tracker/singleEvent.html', { \
		'event': thisEvent, \
    'validDates': vDates, \
    'discussions': discos, \
  })

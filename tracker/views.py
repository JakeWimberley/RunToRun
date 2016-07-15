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
from .models import Discussion, Event, Pin, Thread
from .forms import ThreadForm, DiscussionFormTextOnly, EventForm
import datetime
import pytz
import re

# Create your views here.

def home(request):
	timelineEvents = Event.objects.filter(Q(owner=request.user)|Q(isPublic=True))
	pinned = Pin.objects.filter(owner=request.user)
	return render(request, 'tracker/home.html', { \
    'timelineEvents': timelineEvents, \
    'pinned': pinned, \
    'newThread': ThreadForm(eventChoices=pinned), \
    'newEvent': EventForm(), \
  })

def newThread(request):
# TODO on this view, eventChoices should be set to all public events that the valid time falls in
	pinned = Pin.objects.filter(owner=request.user)
	if request.method == 'POST':
		newThread = ThreadForm(request.POST,eventChoices=pinned)
		if newThread.is_valid():
			_validDate = newThread.cleaned_data['_validDate']
			_validTime = newThread.cleaned_data['_validTime']
			_title = newThread.cleaned_data['_title']
			_text = newThread.cleaned_data['_text']
			_valid = datetime.datetime.combine(_validDate,_validTime)
			_valid = _valid.replace(tzinfo=pytz.UTC)
			# make discussion object, then add it to a new thread object
			discoObj = Discussion(author=request.user,text=_text)
			discoObj.save()
			threadObj = Thread(title=_title,validDate=_valid)
			threadObj.save()
			threadObj.discussions.add(discoObj)
			threadObj.save()
			_eventIds = newThread.cleaned_data['_event']
			for e in _eventIds:
				Event.objects.get(id=e).threads.add(threadObj)
			return HttpResponseRedirect('/thread/{0:d}/'.format(threadObj.pk))
	else:
		newThread = ThreadForm(eventChoices=pinned)
	return render(request, 'tracker/newThread.html', { \
    'newThreadForm': newThread \
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

def extendThread(request, _id):
	"A standalone discussion form with the validDate and event defined by an existing discussion."
	parent = Thread.objects.get(pk=_id)
	_valid = parent.validDate
	if request.method == 'POST':
		newDiscussion = DiscussionFormTextOnly(request.POST)
		if newDiscussion.is_valid():
			_text = newDiscussion.cleaned_data['_text']
			discoObj = Discussion(author=request.user,text=_text)
			discoObj.save()
			parent.discussions.add(discoObj)
			parent.save()
			return HttpResponseRedirect('/thread/{0:d}/'.format(parent.pk))
	else:
		textBox = DiscussionFormTextOnly()
	return render(request, 'tracker/extendThread.html', {
		'id': _id,
		'threadTitle': parent.title,
		'validTime': _valid,
		'discussionTextBox': textBox,
	})

def allDiscussions(request):
	vTimes = [x['validDate'] for x in Discussion.objects.all().order_by('validDate').values('validDate').annotate(Count('validDate',distinct=True))]
	discos = {}
	for vTime in vTimes:
		discos[vTime] = Discussion.objects.filter(validDate=vTime).order_by('-createdDate')
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
			if _startDate and _startTime and _endDate and _endTime:
				_start = datetime.datetime.combine(_startDate,_startTime).replace(tzinfo=pytz.UTC)
				_end = datetime.datetime.combine(_endDate,_endTime).replace(tzinfo=pytz.UTC)
				obj = Event(owner=request.user,title=_title,startDate=_start,endDate=_end,isPublic=_isPublic,isPermanent=_isPermanent)
			else:
				obj = Event(owner=request.user,title=_title,isPublic=_isPublic,isPermanent=_isPermanent)
			obj.save()
			_isPinned = newEvent.cleaned_data['_isPinned']
			if _isPinned:
				pin = Pin(owner=request.user,event=obj)
				pin.save()
			return HttpResponseRedirect('/event/{0:d}/'.format(obj.id))
	else:
		newEvent = EventForm()
	return render(request, 'tracker/newEvent.html', { \
    'newEventForm': newEvent \
  })

def singleEvent(request, _id):
	thisEvent = Event.objects.get(id=_id)
	eventThreads = thisEvent.threads.all()
	threadKeys = [x['id'] for x in eventThreads.values('id').order_by('validDate')]
	discussions = {}
	threadTitles = {}
	validDates = {}
	discos = {}
	for key in threadKeys:
		discussions[key] = eventThreads.get(id=key).discussions.all().order_by('-createdDate')
		threadTitles[key] = eventThreads.get(id=key).title
		validDates[key] = eventThreads.get(id=key).validDate
	pinStatus = Pin.objects.filter(event=thisEvent.pk).exists()
	return render(request, 'tracker/singleEvent.html', { \
		'event': thisEvent, \
		'eventIsPinned': pinStatus, \
		'threadKeys': threadKeys, \
		'discussionSets': discussions, \
		'threadTitles': threadTitles, \
		'validDates': validDates, \
  })

def singleThread(request, _id):
	thisThread = Thread.objects.get(pk=_id)
	threadKeys = {}
	discussions = {}
	threadTitles = {}
	validDates = {}
	threadKeys[_id] = thisThread.pk
	discussions[_id] = thisThread.discussions.all().order_by('-createdDate')
	threadTitles[_id] = thisThread.title
	validDates[_id] = thisThread.validDate
	return render(request, 'tracker/singleThread.html', { \
		'threadKeys': threadKeys, \
		'discussionSets': discussions, \
		'threadTitles': threadTitles, \
		'validDates': validDates, \
  })

def asyncTogglePin(request):
	# TODO user auth (respond with 'not logged in' or something)
	if request.method == 'GET':
			eventId = request.GET['event']
			thisEvent = Event.objects.get(id=eventId)
			pinQs = Pin.objects.filter(event=thisEvent.pk)
			if pinQs.exists():
				# remove pin
				pinQs.delete()
				return HttpResponse('unpinned')
			else:
				pin = Pin(owner=request.user,event=thisEvent)
				pin.save()
				return HttpResponse('pinned')

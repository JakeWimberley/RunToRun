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
from django.db.models import Q, Count, Max, Min
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from .models import Discussion, Event, Pin, Thread, Tag
from .forms import ThreadForm, DiscussionFormTextOnly, EventForm, ChangeEventForm, ChangeThreadForm
import datetime
import pytz
import re


@login_required
def home(request):
    timelineEvents = Event.objects.filter(Q(owner=request.user) | Q(isPublic=True))
    pinned = Pin.objects.filter(owner=request.user)
    recentDate = datetime.datetime.now().replace(tzinfo=pytz.UTC) - datetime.timedelta(days=3)
    # recentThreads is any thread with a discussion written by this user, and that was created since recentDate
    recentThreads = Thread.objects.filter(discussions__author=request.user, discussions__createdDate__gte=recentDate).annotate(lastEdit=Max('discussions__createdDate')).order_by('-lastEdit')
    tags = Tag.objects.all().annotate(numEvents=Count('events'))
    tagScale = tags.aggregate(Max('numEvents'))['numEvents__max'] # number of events in most popular tag
    tagDisplaySizes = {}
    # scale tags based on popularity
    for tag in tags:
        frac = tag.events.count() / float(tagScale)
        tagDisplaySizes[tag.name] = int(frac * 5)
    return render(request, 'tracker/home.html', { \
        'timelineEvents': timelineEvents, \
        'pinned': pinned, \
        'recentThreads': recentThreads, \
        'newThread': ThreadForm(eventChoices=[x.event for x in pinned], selectedChoice=None), \
        'newEvent': EventForm(), \
        'tags': tags, \
        'tagDisplaySizes': tagDisplaySizes, \
    })

@login_required
def newThread(request, setEvent=None):
    formAction = ''
    # setEvent is ID of the event to which this thread should be added
    # if set, also redirect to event page, not thread page
    if request.method == 'POST':
        if setEvent is None:
            newThread = ThreadForm(request.POST, eventChoices=Pin.objects.filter(owner=request.user), selectedChoice=None)
        else:
            newThread = ThreadForm(request.POST, eventChoices=Event.objects.filter(id=setEvent), selectedChoice=setEvent)
        if newThread.is_valid():
            _validDate = newThread.cleaned_data['_validDate']
            _validTime = newThread.cleaned_data['_validTime']
            _title = newThread.cleaned_data['_title']
            _text = newThread.cleaned_data['_text']
            _isExtensible = newThread.cleaned_data['_isExtensible']
            _valid = datetime.datetime.combine(_validDate, _validTime)
            _valid = _valid.replace(tzinfo=pytz.UTC)
            # make discussion object, then add it to a new thread object
            discoObj = Discussion(author=request.user, text=_text)
            discoObj.save()
            threadObj = Thread(title=_title, validDate=_valid, isExtensible=_isExtensible)
            threadObj.save()
            threadObj.discussions.add(discoObj)
            threadObj.save()
            _eventIds = newThread.cleaned_data['_event']
            for e in _eventIds:
                Event.objects.get(id=e).threads.add(threadObj)
            if setEvent is None:
                return HttpResponseRedirect('/thread/{0:d}'.format(threadObj.pk))
            else:
                return HttpResponseRedirect('/event/' + setEvent)
    else:
        # TODO eventChoices should be set to all public events that the valid time falls in
        if setEvent is None:
            newThread = ThreadForm(eventChoices=Pin.objects.filter(owner=request.user), selectedChoice=None)
            formAction = '/newThread/'
        else:
            # specified event must be public, or owned by user, in order to continue
            eventsRequested = Event.objects.filter(id=setEvent)
            if eventsRequested[0].owner == request.user or eventsRequested[0].isPublic:
                newThread = ThreadForm(eventChoices=eventsRequested, selectedChoice=setEvent)
                formAction = '/newThreadInEvent/' + setEvent
            else:
                return render(request, 'tracker/accessDenied.html', {
                    'reason': 'This event belongs to another user, and that user has chosen to keep it private.'
                })
    return render(request, 'tracker/newThread.html', { \
        'action': formAction, \
        'newThreadForm': newThread \
    })

def discussionRange(request, _timeFrom, _timeTo):
    timePattern = re.compile(r'(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)')
    tF = timePattern.match(_timeFrom)
    tT = timePattern.match(_timeTo)
    if tF and tT:
        timeFrom = datetime.datetime(int(tF.group(1), 10), int(tF.group(2), 10), int(tF.group(3), 10), int(tF.group(4), 10), int(tF.group(5), 10), second=0, tzinfo=pytz.UTC)
        timeTo = datetime.datetime(int(tT.group(1), 10), int(tT.group(2), 10), int(tT.group(3), 10), int(tT.group(4), 10), int(tT.group(5), 10), second=59, tzinfo=pytz.UTC)
# timeTo = datetime.datetime(tT.match(1),tT.match(2),tT.match(3),tT.match(4),tT.match(5),tzinfo=pytz.UTC)
        vDates = [v['validDate'] for v in Discussion.objects.filter(validDate__gte=timeFrom, validDate__lte=timeTo).order_by('validDate').values('validDate').annotate(Count('validDate', distinct=True))]
        discos = {}
        for vDate in vDates:
            discos[vDate] = Discussion.objects.filter(validDate=vDate).order_by('-createdDate')
    return render(request, 'tracker/discussionRange.html', { \
        'validDates': vDates, \
        'discussions': discos, \
        'timeFrom': timeFrom, \
        'timeTo': timeTo
    })

@login_required
def extendThread(request, _id):
    "A standalone discussion form with the validDate and event defined by an existing discussion."
    parent = Thread.objects.get(pk=_id)
    # TODO probably should let user extend own threads even if !isExtensible
    if not parent.isExtensible:
        return render(request, 'tracker/accessDenied.html', {
            'reason': 'This thread has been frozen by its steward.'
        })
    _valid = parent.validDate
    if request.method == 'POST':
        newDiscussion = DiscussionFormTextOnly(request.POST)
        if newDiscussion.is_valid():
            _text = newDiscussion.cleaned_data['_text']
            discoObj = Discussion(author=request.user, text=_text)
            discoObj.save()
            parent.discussions.add(discoObj)
            parent.save()
            return HttpResponseRedirect('/thread/{0:d}'.format(parent.pk))
    else:
        textBox = DiscussionFormTextOnly()
    return render(request, 'tracker/extendThread.html', {
        'id': _id,
        'threadTitle': parent.title,
        'validTime': _valid,
        'discussionTextBox': textBox,
    })

def allDiscussions(request):
    vTimes = [x['validDate'] for x in Discussion.objects.all().order_by('validDate').values('validDate').annotate(Count('validDate', distinct=True))]
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

@login_required
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
                _start = datetime.datetime.combine(_startDate, _startTime).replace(tzinfo=pytz.UTC)
                _end = datetime.datetime.combine(_endDate, _endTime).replace(tzinfo=pytz.UTC)
                obj = Event(owner=request.user, title=_title, startDate=_start, endDate=_end, isPublic=_isPublic, isPermanent=_isPermanent)
            else:
                obj = Event(owner=request.user, title=_title, isPublic=_isPublic, isPermanent=_isPermanent)
            obj.save()
            _threadIds = newEvent.cleaned_data['_threadChoices']
            for t in _threadIds:
                threadObj = Thread.objects.get(pk=t)
                obj.threads.add(threadObj)
            _isPinned = newEvent.cleaned_data['_isPinned']
            if _isPinned:
                pin = Pin(owner=request.user, event=obj)
                pin.save()
            return HttpResponseRedirect('/event/{0:d}'.format(obj.id))
    else:
        newEvent = EventForm()
    return render(request, 'tracker/newEvent.html', { \
        'newEventForm': newEvent \
    })


class ChangeEvent(UpdateView):
    template_name = 'tracker/changeEvent.html'
    form_class = ChangeEventForm
    model = Event

    def form_valid(self, form):
        if self.request.user.is_authenticated: 
            if self.request.user == self.object.owner:
                self.object = form.save()
                return HttpResponseRedirect('/event/{0:d}'.format(self.object.pk))
            else:
                return render(self.request, 'tracker/accessDenied.html', {
                    'reason': 'You are not allowed to change an event you don\'t own.'
                })
        else:
            return render(self.request, 'tracker/accessDenied.html', {
                'reason': 'Yaint logged in.'
            })
        return super(ChangeEvent, self).form_valid(form)


class ChangeThread(UpdateView):
    template_name = 'tracker/changeEvent.html'
    form_class = ChangeThreadForm
    model = Thread

    def form_valid(self, form):
        if self.request.user.is_authenticated: 
            if not self.object.isExtensible:
                return render(self.request, 'tracker/accessDenied.html', {
                    'reason': "This thread has been frozen, and must be unfrozen by its steward to allow changes."
                })
            elif self.request.user == getThreadSteward(self.object):
                self.object = form.save()
                return HttpResponseRedirect('/thread/{0:d}'.format(self.object.pk))
            else:
                return render(self.request, 'tracker/accessDenied.html', {
                    'reason': "You are not allowed to change a thread for which you aren't the steward."
                })
        else:
            return render(self.request, 'tracker/accessDenied.html', {
                'reason': 'Yaint logged in.'
            })
        return super(ChangeThread, self).form_valid(form)


@login_required
def singleEvent(request, _id):
    thisEvent = Event.objects.get(id=_id)
    # if event is private, and user is not the owner, don't show
    if not thisEvent.isPublic and thisEvent.owner != request.user:
        return render(request, 'tracker/accessDenied.html', {
            'reason': 'The owner of this event has chosen to keep it private. Other users are not allowed to view it.'
        })
    eventThreads = thisEvent.threads.all()
    threadKeys = [x['id'] for x in eventThreads.values('id').order_by('validDate')]
    discussions = {}
    threadTitles = {}
    validDates = {}
    extensibility = {}
    discos = {}
    allowEdits = {}
    for key in threadKeys:
        thisThread = eventThreads.get(id=key)
        discussions[key] = thisThread.discussions.all().order_by('-createdDate')
        threadTitles[key] = thisThread.title
        validDates[key] = thisThread.validDate
        extensibility[key] = thisThread.isExtensible
        allowEdits[key] = False
        if getThreadSteward(thisThread) == request.user:
            allowEdits[key] = True
    pinStatus = Pin.objects.filter(event=thisEvent.pk).exists()
    return render(request, 'tracker/singleEvent.html', { \
        'event': thisEvent, \
        'eventIsPinned': pinStatus, \
# TODO security to prevent malicious JS from being put into tagList
        'eventTagList': ','.join([str(x) for x in thisEvent.tag_set.all()]), \
        'fullTagList': ','.join([str(x) for x in Tag.objects.all()]), \
        'threadKeys': threadKeys, \
        'discussionSets': discussions, \
        'threadTitles': threadTitles, \
        'validDates': validDates, \
        'extensibility': extensibility, \
        'allowEdits': allowEdits, \
    })

@login_required
def singleTag(request, tagName):
    try:
        thisTag = Tag.objects.get(name=tagName)
        relEvents = thisTag.events.all()
        someArePrivate = thisTag.events.filter(isPublic=False).count() > 0
    except:
        relEvents = None
        someArePrivate = False
    return render(request, 'tracker/multipleEvent.html', { \
        'events': relEvents, \
        'someArePrivate': someArePrivate,
    })


@login_required
def singleThread(request, _id):
    thisThread = Thread.objects.get(pk=_id)
    relEvents = thisThread.event_set.all()
    steward = getThreadSteward(thisThread)
    if not threadIsAccessible(thisThread, request.user):
        return render(request, 'tracker/accessDenied.html', {
            'reason': 'Another user is the steward of this thread, and that user has not made it part of any public event.'
        })
    threadKeys = {}
    discussions = {}
    threadTitles = {}
    validDates = {}
    extensibility = {}
    threadKeys[_id] = thisThread.pk
    discussions[_id] = thisThread.discussions.all().order_by('-createdDate')
    threadTitles[_id] = thisThread.title
    validDates[_id] = thisThread.validDate
    extensibility[_id] = thisThread.isExtensible
    allowEdits = {}
    allowEdits[_id] = False
    if steward == request.user:
        allowEdits[_id] = True
    return render(request, 'tracker/singleThread.html', { \
        'relEvents': relEvents, \
        'threadKeys': threadKeys, \
        'discussionSets': discussions, \
        'threadTitles': threadTitles, \
        'extensibility': extensibility, \
        'validDates': validDates, \
        'allowEdits': allowEdits, \
    })

def asyncTogglePin(request):
    '''
    Toggle pinned status of event with its ID specified in GET field 'event'.
    Returns status 400 and the word 'unauthenticated' if user is not logged in.
    Otherwise returns the word 'pinned' or 'unpinned'
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('unauthenticated')
    if request.method == 'GET':
        eventId = request.GET['event']
        thisEvent = Event.objects.get(id=eventId)
        pinQs = Pin.objects.filter(event=thisEvent.pk)
        if pinQs.exists():
            # remove pin
            pinQs.delete()
            return HttpResponse('unpinned')
        else:
            pin = Pin(owner=request.user, event=thisEvent)
            pin.save()
            return HttpResponse('pinned')

def asyncToggleTag(request):
    '''
    Add/remove tag from an event with specified ID. GET fields 'event' and 'tagName'.
    Returns status 400 and an empty string if user is not logged in.
    Returns status 404 if event with specified ID does not exist.
    Returns status 403 if event is not owned by user and is not public.
    Otherwise returns the new list of tags
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest()
    if request.method == 'GET':
        eventId = request.GET['event']
        tagName = request.GET['tagName']
        # remove any funky chars and/or surrounding whitespace from tagName
        tagName = tagName.replace(',', '-').replace('\\', '/').replace("'", '`').strip()
        try:
            eventObj = Event.objects.get(pk=eventId)
        except Event.DoesNotExist: # 404
            return HttpResponseNotFound()
        if request.user != eventObj.owner: # 403
            return HttpResponseForbidden()
        try:
            tagObj = Tag.objects.get(name=tagName)
        except Tag.DoesNotExist:
            # create new tag for this event
            newTag = Tag(name=tagName)
            newTag.save()
            newTag.events.add(eventObj)
        else:
            if eventObj in tagObj.events.all():
                # untag event (remove its id from tag object)
                tagObj.events.remove(eventObj)
            else:
                # tag event
                tagObj.events.add(eventObj)
        # return comma-delimited list of tags
        return HttpResponse(','.join([str(x) for x in eventObj.tag_set.all()]))

def asyncThreadsForPeriod(request):
    '''
    Get a JSON object representing threads that fall in the specified period (GET fields 'from' and 'to').
    Returns status 400 and an empty string if user is not logged in.
    Otherwise returns JSON object mapping thread IDs to their names.
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest()
    if request.method == 'GET':
        timePattern = re.compile(r'(\d{4})-?(\d\d)-?(\d\d)_(\d\d):?(\d\d)')
        tF = timePattern.match(request.GET['from'])
        tT = timePattern.match(request.GET['to'])
        if tF and tT:
            timeFrom = datetime.datetime(int(tF.group(1), 10), int(tF.group(2), 10), int(tF.group(3), 10), int(tF.group(4), 10), int(tF.group(5), 10), second=0, tzinfo=pytz.UTC)
            timeTo = datetime.datetime(int(tT.group(1), 10), int(tT.group(2), 10), int(tT.group(3), 10), int(tT.group(4), 10), int(tT.group(5), 10), second=59, tzinfo=pytz.UTC)
        else:
            return
        # return json obj of id's and names (so JS in template can make listbox)
        resp = {}
        for t in Thread.objects.filter(validDate__gte=timeFrom,validDate__lte=timeTo).order_by('validDate'):
            if threadIsAccessible(t,request.user): resp["{0:d}".format(t.id)] = str(t)
        return JsonResponse(resp)

def asyncEventsAtTime(request):
    '''
    Get a JSON object representing events that span the specified point in time (GET field 'when').
    GET field 'threadId' can optionally be set to indicate which event(s) are already associated with that thread.
    Returns status 400 and an empty string if user is not logged in.
    Otherwise returns JSON object mapping thread IDs to their names.
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest()
    if request.method == 'GET':
        timePattern = re.compile(r'(\d{4})-?(\d\d)-?(\d\d)_(\d\d):?(\d\d)')
        when = timePattern.match(request.GET['when'])
        if when:
            timePoint = datetime.datetime(int(when.group(1), 10), int(when.group(2), 10), int(when.group(3), 10), int(when.group(4), 10), int(when.group(5), 10), second=0, tzinfo=pytz.UTC)
        else:
            return
        if request.GET['threadId'] is not None:
            specThread = Thread.objects.get(id=request.GET['threadId'])
        # return json obj mapping pk to identifying info
        resp = {}
        for e in Event.objects.filter(startDate__lte=timePoint,endDate__gte=timePoint).order_by('startDate'):
            threadStatus = False # initially assume not associated with event
            if specThread in e.threads.all(): threadStatus = True
            if e.owner == request.user or e.isPublic:
                resp["{0:d}".format(e.pk)] = [e.title, str(e.owner), threadStatus]
        return JsonResponse(resp)
    
def asyncToggleFrozen(request):
    '''
    Toggle isExtensible on the thread with its ID specified in GET field 'thread'.
    Returns status 400 and the word 'unauthenticated' if user is not logged in.
    Otherwise returns the string 'frozen' or 'unfrozen' to indicate the new value
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('unauthenticated')
    if request.method == 'GET':
        threadId = request.GET['thread']
        thisThread = Thread.objects.get(id=threadId)
        if thisThread.isExtensible:
            thisThread.isExtensible = False
            thisThread.save()
            return HttpResponse('frozen')
        else:
            thisThread.isExtensible = True
            thisThread.save()
            return HttpResponse('unfrozen')

def asyncAssociateEventsWithThread(request):
    '''
    Associate events (GET array newRelations) with thread (GET threadId).
    Also must have GET field allMatchingEvents (all events that were represented in the form)
    Returns status 400 and an empty string if user is not logged in.
    Returns status 404 if event with specified ID does not exist.
    Returns status 403 if user is not allowed to change event or thread.
    Otherwise returns 204 (success, but no data to return)
    '''
    if not request.user.is_authenticated():
        return HttpResponseBadRequest()
    if request.method == 'GET':
        threadId = request.GET['threadId']
        selectedEventArray = request.GET.getlist('newRelations')
        allEventArray = request.GET['allMatchingEvents'].split(',')
        try:
            threadObj = Thread.objects.get(pk=threadId)
        except Thread.DoesNotExist: # 404
            return HttpResponseNotFound()
        if request.user != getThreadSteward(threadObj): # 403
            return HttpResponseForbidden()
        eventObjList = {}
        # check that all the events exist -- if not don't make any changes
        for eId in allEventArray:
            try:
                eventObjList[eId] = Event.objects.get(pk=eId)
                if request.user != eventObjList[eId].owner: # 403
                    return HttpResponseForbidden()
            except Event.DoesNotExist:
                return HttpResponseNotFound()
        # Must first remove the thread from all events that were in the form,
        # then add it back to the ones that were checked
        for eId in allEventArray:
            eventObj = eventObjList[eId]
            if threadObj in eventObj.threads.all():
                eventObj.threads.remove(threadObj)
        for eId in selectedEventArray:
            eventObj = eventObjList[eId]
            eventObj.threads.add(threadObj)
        return HttpResponse(status=204)
    else:
        return HttpResponseBadRequest()

def getThreadSteward(thread):
    # the author of the first discussion is considered the "owner" or "steward" of the thread
    minPk = thread.discussions.all().aggregate(Min("pk"))
    return thread.discussions.get(pk=minPk['pk__min']).author

def threadIsAccessible(thread, user):
    # if user is not steward of thread, check events to see if thread is part of a public event
    # if not, return false to indicate access should be denied
    if getThreadSteward(thread) == user:
        return True
    else:
        for event in thread.event_set.all():
            if event.isPublic: return True
    return False

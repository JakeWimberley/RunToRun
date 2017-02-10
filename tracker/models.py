"""
    Copyright 2016 Jacob C. Wimberley.

    This file is part of Weathredds.

    Weathredds is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Weathredds is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Weathredds.  If not, see <http://www.gnu.org/licenses/>.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

dateFormatStr = '%H%Mz %a %b %d'

# class UserInterface(models.Model):
# https://docs.djangoproject.com/en/1.9/topics/auth/customizing/#extending-user
# https://djangosnippets.org/snippets/1261/
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     colorFore = ColorField(blank=True)
#     colorBack = ColorField(blank=True)

class Pin(models.Model):
    owner = models.ForeignKey('auth.User')
    event = models.ForeignKey('Event')

    def __unicode__(self):
        return unicode(self.event)

class Chart(models.Model):
    validDate = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to='charts')
    isArchived = models.BooleanField(default=False)

class Discussion(models.Model):
    author = models.ForeignKey('auth.User')
    createdDate = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def __str__(self):
        return self.author.username + ', ' + self.createdDate.strftime(dateFormatStr)

class Thread(models.Model):
    title = models.TextField()
    validDate = models.DateTimeField(default=timezone.now)
    discussions = models.ManyToManyField(Discussion, blank=True)
    isExtensible = models.BooleanField(default=True)

    def __str__(self):
        return self.title + ' (' + self.validDate.strftime(dateFormatStr) + ')'

class Event(models.Model):
# TODO summary and conclusion (isConcluded)
    title = models.CharField(max_length=120)
    createdDate = models.DateTimeField(default=timezone.now)
    startDate = models.DateTimeField(null=True, blank=True, verbose_name='start date (if blank, event time range is defined by that of threads)')
    endDate = models.DateTimeField(null=True, blank=True, verbose_name='end date (only used if start date is defined)')
    owner = models.ForeignKey('auth.User')
    threads = models.ManyToManyField(Thread, blank=True)
    isPublic = models.BooleanField(default=False, verbose_name='share this event with other users')
    isPermanent = models.BooleanField(default=False, verbose_name="keep this event forever")

    def describeTimeRange(self):
        # start/end dates are preferred if user defined them
        if self.startDate and self.endDate:
            return unicode('{0:s} to {1:s} [fixed by owner]'.format(self.startDate.strftime(dateFormatStr), self.endDate.strftime(dateFormatStr)))
        allThreadDates = [x.validDate for x in self.threads.all()]
        allThreadDates.sort()
        if len(allThreadDates) >= 2:
            return unicode('{0:s} to {1:s}'.format(allThreadDates[0].strftime(dateFormatStr), allThreadDates[-1].strftime(dateFormatStr)))
        elif len(allThreadDates) == 1:
            return unicode('{0:s} [single thread]'.format(allThreadDates[0].strftime(dateFormatStr)))
        else:
            return unicode('undefined time range')

    def __unicode__(self):
        return self.title + u' (' + self.describeTimeRange() + u')'

class Tag(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    events = models.ManyToManyField(Event, blank=True)

    def __unicode__(self):
        return self.name

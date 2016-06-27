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
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

dateFormatStr = '%H%Mz %a %b %d'

#class UserInterface(models.Model):
# https://docs.djangoproject.com/en/1.9/topics/auth/customizing/#extending-user
# https://djangosnippets.org/snippets/1261/
#	user = models.OneToOneField(User, on_delete=models.CASCADE)
#	colorFore = ColorField(blank=True)
#	colorBack = ColorField(blank=True)

class Pin(models.Model):
	owner = models.ForeignKey('auth.User')
	event = models.ForeignKey('Event')

	def __str__(self):
		return str(self.event)

class Chart(models.Model):
	validDate = models.DateTimeField(default=timezone.now)
	title = models.CharField(max_length=120)
	description = models.TextField()
	image = models.ImageField(upload_to='charts')
	isArchived = models.BooleanField(default=False)

class Discussion(models.Model):
	author = models.ForeignKey('auth.User')
	validDate = models.DateTimeField(default=timezone.now)
	text = models.TextField()

	def __str__(self):
		return self.author.username + ' at ' + self.validDate.strftime(dateFormatStr)

class Event(models.Model):
	title = models.CharField(max_length=120)
	createdDate = models.DateTimeField(default=timezone.now)
	owner = models.ForeignKey('auth.User')
	discussions = models.ManyToManyField(Discussion,verbose_name='discussion timeline',blank=True)
	isPublic = models.BooleanField(default=False,verbose_name='share this event with other users')
	isPermanent = models.BooleanField(default=False,verbose_name="keep this event forever")

	def __str__(self):
		allDiscussionDates = [x.validDate for x in self.discussions.all()]
		allDiscussionDates.sort()
		if len(allDiscussionDates) >= 2:
			return '{0:s} ({1:s} to {2:s})'.format(self.title, allDiscussionDates[0].strftime(dateFormatStr), allDiscussionDates[-1].strftime(dateFormatStr))
		elif len(allDiscussionDates) == 1:
			return '{0:s} ({1:s})'.format(self.title, allDiscussionDates[0].strftime(dateFormatStr))
		else:
			return '{0:s} (no discussions)'.format(self.title)

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
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    #url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logged_out.html'}, name='logout'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    #url(r'^', include('django.contrib.auth.urls')),
#url(r'^discussions/(\d{8}_\d{4})/(\d{8}_\d{4})/$', views.discussionRange),
#url(r'^discussions/$', views.allDiscussions),
    url(r'^extendThread/(\d+)', views.extendThread, name='extendThread'),
    url(r'^newEvent/$', views.newEvent, name='newEvent'),
    url(r'^newThread/$', views.newThread, name='newThread'),
    url(r'^newThreadInEvent/(\d+)', views.newThread, name='newThreadInEvent'),
    url(r'^event/(\d+)', views.singleEvent, name='singleEvent'),
    url(r'^thread/(\d+)', views.singleThread, name='singleThread'),
    url(r'^tag/([^,\\\']+)', views.singleTag, name='singleTag'),
    url(r'^async/togglePin', views.asyncTogglePin, name='togglePin'),
    url(r'^async/toggleTag', views.asyncToggleTag, name='toggleTag'),
    url(r'^async/threadsForPeriod', views.asyncThreadsForPeriod, name='threadsForPeriod'),
]

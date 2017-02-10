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

from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Event)
admin.site.register(Thread)
admin.site.register(Discussion)
admin.site.register(Chart)
admin.site.register(Pin)
admin.site.register(Tag)

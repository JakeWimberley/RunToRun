from django.contrib import admin
from .models import Event, Discussion, Chart, Pin

# Register your models here.

admin.site.register(Event)
admin.site.register(Discussion)
admin.site.register(Chart)
admin.site.register(Pin)

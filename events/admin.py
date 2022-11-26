from django.contrib import admin
from django.contrib.admin import AdminSite
from events.models import Epic, Event, EventHero, EventVillain
# Register your models here.

class EventAdminSite(AdminSite):
    site_header = "UMSRA Events Admin"
    site_title = "UMSRA Events Admin Portal"
    index_title = "Welcome to UMSRA Researcher Events Portal"

event_admin_site = EventAdminSite(name='event_admin')

# admin.site.register(Epic)
# admin.site.register(Event)
# admin.site.register(EventHero)
# admin.site.register(EventVillain)

event_admin_site.register(Epic)
event_admin_site.register(Event)
event_admin_site.register(EventHero)
event_admin_site.register(EventVillain)

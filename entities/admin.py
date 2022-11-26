from django.contrib import admin
import csv
import sys
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django import forms 

from django.contrib.auth.models import User, Group
from entities.models import Category, Origin, Hero, Villain, HeroAcquaintance
# Register your models here.

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response


class IsVeryBenevolentFilter(admin.SimpleListFilter):
    title = 'is_very_benevolent'
    parameter_name = 'is_very_benevolent'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(benevolence_factor__gt=75)
        elif value == 'No':
            return queryset.exclude(benevolence_factor__gt=75)
        return queryset
    
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

# @admin.register(Origin) # this design make per row in the listview page
# class OriginAdmin(admin.ModelAdmin):
#     list_display = ("name", "hero_count", "villain_count")

#     def hero_count(self, obj):
#         return obj.hero_set.count()

#     def villain_count(self, obj):
#         return obj.villain_set.count()

@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("name", "hero_count", "villain_count")
    actions = ["export_as_csv"]


    def get_queryset(self, request): # override get_queryset is better way
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _hero_count=Count("hero", distinct=True),
            _villain_count=Count("villain", distinct=True),
        )
        return queryset

    def hero_count(self, obj):
        return obj._hero_count

    def villain_count(self, obj):
        return obj._villain_count
    
    # enable sorting on calculated fields
    hero_count.admin_order_field = '_hero_count'
    villain_count.admin_order_field = '_villain_count'


class HeroAcquaintanceInline(admin.TabularInline):
    model = HeroAcquaintance # OneToOneField case


class HeroForm(forms.ModelForm):
    category_name = forms.CharField()

    class Meta:
        model = Hero
        exclude = ["category"]


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "entities/heroes_changelist.html"
    form = HeroForm
    list_per_page = 10 # limitation for larger number of rows on listview page
    # list_per_page = sys.maxsize # disable django admin pagination

    list_display = ("name", "is_immortal", "category", "origin", "is_very_benevolent", "children_display")
    list_filter = ("is_immortal", "category", "origin",IsVeryBenevolentFilter)
    # date_hierarchy = 'added_on' # add date based filtering
    '''
    This can be very costly with a large number of objects. As an alternative, 
    you can subclass SimpleListFilter, 
    and allow filtering only on years or the months.
    '''
    
    actions = ["mark_immortal","export_as_csv"]
    inlines = [HeroAcquaintanceInline]

    def mark_immortal(self, request, queryset):
        queryset.update(is_immortal=True)

    def is_very_benevolent(self, obj):
        return obj.benevolence_factor > 75
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('immortal/', self.set_immortal),
            path('mortal/', self.set_mortal),
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def set_immortal(self, request):
        self.model.objects.all().update(is_immortal=True)
        self.message_user(request, "All heroes are now immortal")
        return HttpResponseRedirect("../")

    def set_mortal(self, request):
        self.model.objects.all().update(is_immortal=False)
        self.message_user(request, "All heroes are now mortal")
        return HttpResponseRedirect("../")
    
    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
            #return HttpResponseRedirect("../")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )
        
    def save_model(self, request, obj, form, change):
        category_name = form.cleaned_data["category_name"]
        category, _ = Category.objects.get_or_create(name=category_name)
        obj.category = category
        super().save_model(request, obj, form, change)
        
    # show many to many or reverse FK fields on listview page
    def children_display(self, obj):
        return ", ".join([
            child.name for child in obj.children.all()
        ])
        
    children_display.short_description = "Children"



    
    # change boolean value to icon
    is_very_benevolent.boolean = True
    

class VillainInline(admin.StackedInline):
    model = Villain
    
# class VillainInline(admin.TabularInline):
#     model = Villain

@admin.register(Category) 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

    inlines = [VillainInline, HeroAcquaintanceInline]
    
    


#admin.site.register(Category)
#admin.site.register(Origin)
#admin.site.register(Hero)
admin.site.register(Villain)
admin.site.register(HeroAcquaintance)

admin.site.unregister(User)
admin.site.unregister(Group)
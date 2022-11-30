from django.contrib import admin
import csv
import sys
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.urls import path
from django import forms
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User, Group
from entities.models import Category, Origin, Hero, Villain, HeroAcquaintance, HeroProxy
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

class CategoryChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "Category: {}".format(obj.name)


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_list_template = "entities/heroes_changelist.html"
    form = HeroForm
    list_per_page = 10 # limitation for larger number of rows on listview page
    # list_per_page = sys.maxsize # disable django admin pagination

    list_display = ("name", "is_immortal", "origin", "is_very_benevolent", "children_display")
    list_filter = ("is_immortal", "category", "origin",IsVeryBenevolentFilter)
    readonly_fields = ["headshot_image",]
    exclude = ['added_by',]
    # date_hierarchy = 'added_on' # add date based filtering
    '''
    This can be very costly with a large number of objects. As an alternative,
    you can subclass SimpleListFilter,
    and allow filtering only on years or the months.
    '''

    # if category has more then 100000 objects, dropdown also be 100000 selections.
    # it will make the page both slow and the dropdown hard to use
    # raw_id_fields will open new page to select one of pk with pagination
    # but it doens't have select input bar, using browser's searching service
    raw_id_fields = ["category"]

    actions = ["mark_immortal","export_as_csv"]
    inlines = [HeroAcquaintanceInline]

    # filter FK dropdown values in django admin
    # make subset using queryset. it show only a, b pk in category
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            #kwargs["queryset"] = Category.objects.filter(name__in=['a', 'b'])

            # following code will make category selection as "Category:***"
            # without this override, it just show pk number
            # if this admin using raw_id_fields, it will ignored
            return CategoryChoiceField(queryset=Category.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # a field editable while creating, but read only in existing objects
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["headshot_image",]
        else:
            return []

    def headshot_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.headshot.url,
            width=obj.headshot.width,
            height=obj.headshot.height,
            )
    )

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
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        category_name = form.cleaned_data["category_name"]
        category, _ = Category.objects.get_or_create(name=category_name)
        obj.category = category
        super().save_model(request, obj, form, change)

    # show many to many or reverse FK fields on listview page
    def children_display(self, obj):
        # return ", ".join([
        #     child.name for child in obj.children.all()
        # ])
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                    reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                    args=(child.pk,)),
                child.name)
             for child in obj.children.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"

    children_display.short_description = "Children"

    # change boolean value to icon
    is_very_benevolent.boolean = True


# add a model twice to Django admin
@admin.register(HeroProxy)
class HeroProxyAdmin(admin.ModelAdmin):
    readonly_fields = ("name", "is_immortal", "category", "origin",)


@admin.register(Villain)
class VillainAdmin(admin.ModelAdmin, ExportCsvMixin):
    change_form_template = "entities/villain_changeform.html"

    # add a custom button to Django change view page
    # this function will 
    def response_change(self, request, obj):
        if "_make-unique" in request.POST:
            matching_names_except_this = self.get_queryset(request).filter(name=obj.name).exclude(pk=obj.id)
            matching_names_except_this.delete()
            obj.is_unique = True
            obj.save()
            self.message_user(request, "This villain is now unique")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


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
#admin.site.register(Villain)
admin.site.register(HeroAcquaintance)

admin.site.unregister(User)
admin.site.unregister(Group)
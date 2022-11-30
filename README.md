# Django-Admin-Cookbook-Study-Project
Django-Admin-Cookbook-Study-Project

# Class Information
-  [Django Admin Cookbook](https://books.agiliq.com/projects/django-admin-cookbook/en/latest/introduction.html)

# google reference
- [Python으로 CSV 파일 읽기/쓰기: csv 모듈 활용법](https://nerogarret.tistory.com/63)
    ```
    import csv

    f = open("data.csv", "r")
    reader = csv.reader(f)

    for row in reader:
        print(row)
    ```
- [Django - 관리자 페이지에서 엑셀 출력 방법: 한글 출력](https://cocook.tistory.com/21)
    ```
    #app -> admin.py 에 다음과 같이 작성한다.
    actions = ["export_as_csv"]

        def export_as_csv(self, request, queryset):

            """ return Export as csv File """

            meta = self.model._meta #모델이름을 불러온다.

            response = HttpResponse(content_type="text/csv")
            #기본 인코딩 방식은 utf-8이므로 한글 출력을 원할때는 아래 주석과 같이 작성한다.
            #response = HttpResponse(content_type="text/csv", charset = 'euc-kr')

            response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)

            writer = csv.writer(response)
            writer.writerow(field_names)
            for obj in queryset:
                row = writer.writerow([getattr(obj, field) for field in field_names])

            return response
    ```

# note
- link : [How to get Django admin urls for specific objects?](https://books.agiliq.com/projects/django-admin-cookbook/en/latest/object_url.html)
```
@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
    ...

    def children_display(self, obj):
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
```
- change url
```
reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name), args=(child.pk,))
```
- delete url
```
reverse('admin:{}_{}_delete'.format(obj._meta.app_label, obj._meta.model_name), args=(child.pk,))
```
- history url
```
reverse('admin:{}_{}_history'.format(obj._meta.app_label, obj._meta.model_name), args=(child.pk,))
```
* * *
- link : [How to add a database view to Django admin](https://books.agiliq.com/projects/django-admin-cookbook/en/latest/database_view.html)
- assume that database has view table.
```
create view entities_entity as
    select id, name from entities_hero
    union
    select 10000+id as id, name from entities_villain
```
- result
```
sqlite> select * from entities_entity;
1|Krishna
2|Vishnu
3|Achilles
4|Thor
5|Zeus
6|Athena
7|Apollo
10001|Ravana
10002|Fenrir
```
- add managed=False model
```
class AllEntity(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "entities_entity"
```
- add admin
```
@admin.register(AllEntity)
class AllEntiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
```
* * *
- link : [How to set ordering of Apps and models in Django admin dashboard.](https://books.agiliq.com/projects/django-admin-cookbook/en/latest/set_ordering.html)
- index function
  - template : admin/index.html
  - view function : ModelAdmin.index
        ```
        def index(self, request, extra_context=None):
            """
            Display the main admin index page, which lists all of the installed
            apps that have been registered in this site.
            """
            app_list = self.get_app_list(request)
            context = {
                **self.each_context(request),
                'title': self.index_title,
                'app_list': app_list,
                **(extra_context or {}),
            }

            request.current_app = self.name

            return TemplateResponse(request, self.index_template or
                'admin/index.html', context)
        ```
- get_app_list function
    ```
    class EventAdminSite(AdminSite):
        def get_app_list(self, request):
            """
            Return a sorted list of all the installed apps that have been
            registered in this site.
            """
            ordering = {
                "Event heros": 1,
                "Event villains": 2,
                "Epics": 3,
                "Events": 4
            }
            app_dict = self._build_app_dict(request)
            # a.sort(key=lambda x: b.index(x[0]))
            # Sort the apps alphabetically.
            app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

            # Sort the models alphabetically within each app.
            for app in app_list:
                app['models'].sort(key=lambda x: ordering[x['name']])

            return app_list
    ```
    - following code fixed ordering
        ```
        app['models'].sort(key=lambda x: ordering[x['name']])
        ```
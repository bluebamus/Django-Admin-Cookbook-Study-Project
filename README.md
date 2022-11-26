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
- 
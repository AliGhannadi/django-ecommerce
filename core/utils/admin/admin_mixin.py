from django.urls import path, reverse
from django.http import HttpResponse
from django.contrib import admin
from django.utils.text import slugify
import csv
import codecs

class EnrichedModelAdmin(admin.ModelAdmin):
    change_list_template = 'admin/change_list.html'

    def custom_action(self, request):
        # Custom action logic
        pass

    def get_urls(self):
        urls = super().get_urls()
        model_name = slugify(self.model._meta.verbose_name_plural)
        custom_urls = [
            path(
                f"{model_name}/export-csv-data/",
                self.admin_site.admin_view(self.export_all_data_csv),
                name="export_csv_data"
            ),
        ]
        return custom_urls + urls

    def export_all_data_csv(self, request):
        model = self.model
        model_name = model._meta.verbose_name_plural
        filename = f"{slugify(model_name)}.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(codecs.getwriter('utf-8')(response))
        model_fields = [field.name for field in model._meta.fields]

        writer.writerow(model_fields)
        objects = model.objects.all()

        for obj in objects:
            row = [str(getattr(obj, field.attname)) for field in model._meta.fields]
            writer.writerow(row)

        return response
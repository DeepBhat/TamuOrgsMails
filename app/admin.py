from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path
import csv
from django.shortcuts import render, redirect
from .models import Exclusion, Organization
from io import TextIOWrapper

admin.site.register([Organization])
admin.site.unregister(User)
admin.site.unregister(Group)

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Exclusion)
class ExclusionAdmin(admin.ModelAdmin):
    change_list_template = "app/exclusion_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES["csv_file"].file,encoding='utf-8')
            reader = csv.reader(csv_file)
            # Create Exclusion objects from passed in data
            for row in reader:
                text = row[0]
                Exclusion.objects.create(text=text)
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )
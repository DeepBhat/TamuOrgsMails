from django.db import models
from django.db.models.fields import CharField, DateField, EmailField, URLField

# Create your models here.

class Organization(models.Model):
    name = CharField(max_length=500, unique=True)
    org_page = URLField(unique=True)
    email = EmailField()
    date_modified = DateField(auto_now=True)
    contact_name = CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name}: {self.email}"

    








from django.test import TestCase
from .models import Organization
from django.db.models import Q
import requests
import re
from bs4 import BeautifulSoup

# Create your tests here.
class InTestCase(TestCase):
    def setUp(self) -> None:
        Organization.objects.create(name="12th man",org_page="www.google.com/1",email="yet@gmail.com")
        Organization.objects.create(name="Not recognized",org_page="www.google.com/2",email="yet@gmail.com")
        Organization.objects.create(name="SASE",org_page="www.google.com/3",email="yeet@gmail.com")


    def test_public_name(self):
        response = BeautifulSoup(requests.get("https://stuactonline.tamu.edu/app/organization/profile/public/id/83").text, features="lxml").get_text()
        public_name = re.findall(r'Public Contact Name:.*\n', response)[0][20:-1]

        self.assertEqual("Bryan Carbajal", public_name)

        
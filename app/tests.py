from django.test import TestCase
from .models import Organization
from django.db.models import Q
import requests
import re

# Create your tests here.
class InTestCase(TestCase):
    def setUp(self) -> None:
        Organization.objects.create(name="12th man",org_page="www.google.com/1",email="yet@gmail.com")
        Organization.objects.create(name="Not recognized",org_page="www.google.com/2",email="yet@gmail.com")
        Organization.objects.create(name="SASE",org_page="www.google.com/3",email="yeet@gmail.com")


    def test_in_works(self):
        mass_str = "12th man other org SASE"
        org = Organization.objects.first()
        self.assertTrue(org.name in mass_str)
        filtered_orgs = Organization.objects.exclude(~Q(name__in=mass_str))
        self.assertGreater(len(filtered_orgs), 0)
        for org in filtered_orgs:
            self.assertFalse(org.name in mass_str)

    def test_in_works_2(self):
        mass_str = "12th man other SASE"
        filtered_orgs = Organization.objects.filter(name__in=mass_str)
        self.assertGreater(len(filtered_orgs), 0)
        for org in filtered_orgs:
            self.assertTrue(org.name in mass_str)
        
    def test_deletion(self):
        mass_str = "12th man other SASE"
        for org in Organization.objects.all():
            if org.name not in mass_str:
                Organization.delete(org)
        
        orgs = Organization.objects.all()
        self.assertEqual(len(orgs),2)

    def test_public_name(self):
        response = requests.get("https://stuactonline.tamu.edu/app/organization/profile/public/id/83")
        public_name = re.findall(r'Public Contact Name:.*Public Contact')
        self.assertEqual(1, len(public_name))
from django.test import TestCase
from .models import Organization
from django.db.models import Q
import requests
import re
from bs4 import BeautifulSoup
import spacy
from collections import Counter
import en_core_web_sm
from pprint import pprint

# Create your tests here.
class InTestCase(TestCase):
    def setUp(self) -> None:
        Organization.objects.create(name="12th man",org_page="www.google.com/1",email="yet@gmail.com")
        Organization.objects.create(name="Not recognized",org_page="www.google.com/2",email="yet@gmail.com")
        Organization.objects.create(name="SASE",org_page="www.google.com/3",email="yeet@gmail.com")


    def test_public_name(self):
        response = BeautifulSoup(requests.get("https://stuactonline.tamu.edu/app/organization/profile/public/id/83").text, features="lxml").get_text()
        public_name = re.findall(r'Public Contact Name:.*\n', response)[0][20:-1]

        # self.assertEqual("Bryan Carbajal", public_name)
    
    def test_spacy(self):
        potential_names = ['Sam Merriweather', 'Nikhil Goud Jadapolu', 'Ryllies Co-Presidents', 
        'SWISE President', 'Blanche ter Hofstede', 'Kilvain Phillip - Chief Student Leader', 'TAMU WIA',
        'JP Harris', 'Garrison Bowling', 'Clyde Maurice Swann III', 'Officers', 'Paramdeep Singh',
        'Aggie School Volunteers', 'Dr. Koufteros', 'ASHRD', 'Alisa Isaac (President)', 'Hagan Dalton (Captain)',
        'Patrick Hernandez/Macy Birden', 'President: Cecile Savoie or Vice President: Jake Marines']

        nlp = en_core_web_sm.load()
        for potential_name in potential_names:
            doc = nlp(potential_name)
            pprint([(X.text, X.label_) for X in doc.ents if X.label_ == 'PERSON'])




        
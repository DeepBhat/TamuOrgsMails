from django.shortcuts import render
from .models import Organization
from django.http import HttpResponse
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
from django.db.utils import IntegrityError
import asyncio
from asgiref.sync import sync_to_async
import csv
from .forms import DateForm

# Create your views here.
def index(request): 
    # get all orgs
    orgs = Organization.objects.all().order_by('-date_modified')

    context = {
        'orgs': orgs,
        'orgs_length': len(orgs)
    }

    return render(request, 'app/index.html', context)

@sync_to_async
def update_database():
    print("Updating database...")
    url = "https://stuactonline.tamu.edu/app/search/index/index/search/name?q="


    # read the table data
    orgs_list_raw = pd.read_html(url)[0][1].tolist()
    orgs_list_recognized = list(filter(lambda org_text: "Not Recognized" not in org_text, orgs_list_raw))
    orgs_list_str = "".join(orgs_list_recognized)

    print("Got recognized orgs...")

    # remove all the orgs in the database that are not recognized
    for org in Organization.objects.all():
            if org.name not in orgs_list_str:
                print(f"Deleting {org.name}")
                Organization.delete(org)

    # get all the anchor tags
    response = requests.get(url).text
    soup = BeautifulSoup(response)
    anchor_tags = [str(anchor_tag) for anchor_tag in soup.find_all("a")]
    print("Got anchor tags...")

    # extract the link and name from the anchor tags, keeping only the recognized org links
    for anchor_tag in anchor_tags:
        # find all anchor tags and the corresponding name
        links = re.findall(r'(https://stuactonline.tamu.edu/app/organization/index/index/id/.*")', anchor_tag)
        link = None
        if links: 
            link = links[0][:-1]
            name = None
            names = re.findall(r'">.*</a>', anchor_tag)
            if names:
                name = names[0][2:-4]
                # fix &amp; to &
                if '&amp;' in name:
                    name = name.replace("&amp;","&")
                if name in orgs_list_str:
                    # it is a recognized org and we have the link
                    exists = False
                    # check if the name is in database and was modified in the last 30 days.
                    # if true, skip the updation or addition. Set a flag exists
                    try:
                        org = Organization.objects.get(name = name)
                        exists = True
                        # only update if it hasnt been updated in the past 30 days
                        if (date.today() - org.date_modified).days <= 30:
                            continue
                    except Organization.DoesNotExist:
                        exists = False

                    # visit the link of the org to extract the email
                    response = requests.get(link).text

                    # extract the mail address from the page
                    if mail_address := re.findall(r'"mailto:.*"', response):
                        mail_address = mail_address[0][8:-1]

                        # if mail address found, add or update the email and link
                        # depending on if it exists or not
                        dirty = False
                        if exists:
                            org = Organization.objects.get(name = name)
                            # if either email or link has changed, update them
                            if org.email != mail_address:
                                org.email = mail_address
                                dirty = True
                            if org.org_page != link:
                                org.org_page = link
                                dirty = True
                            if dirty:
                                print(f"Updating entry: {name}")
                        else:
                            # if org doesnt exist create it
                            org = Organization(name = name, email = mail_address, org_page = link)
                            dirty = True
                            print(f"Adding new entry: {name}")
                        
                        try:
                            # if the org has been created or modified, save it
                            if dirty:
                                org.save()
                        except IntegrityError:
                            print(f"email integrity error={mail_address}")
           
    print("Done updating, exiting...")


async def update(request):
    asyncio.create_task(update_database())
    return HttpResponse("Your request has been acknowledged. Check back in several minutes to see the updated database.")

def download_csv(request, date=None):
    # return the name and emails as csv file
    output = []
    response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename="Student Org Emails.csv"'})
    writer = csv.writer(response)
    if date:
        orgs = Organization.objects.filter(date_modified=date)
    else:
        orgs = Organization.objects.all()
    #Header
    writer.writerow(['Name', 'Email'])
    for org in orgs:
        output.append([org.name, org.email])
    #CSV Data
    writer.writerows(output)
    return response

def mass_email(request):
    if request.method == 'GET':
        # get all orgs
        orgs = Organization.objects.all()
        # generate the clean form
        form = DateForm()
    elif request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            date_selected = form.cleaned_data["date_selected"]
            # filter based on date input
            if form.cleaned_data["csv_download"]:
                return download_csv(request=request, date=form.cleaned_data["date_selected"])
            orgs = Organization.objects.filter(date_modified=date_selected)

    # generate a mass email mailto: link
    mass_email_queries = [f"mailto:?bcc="]
    
    # only works with 2056 characters at once
    org_index = 0
    query_index = 0
    while org_index < len(orgs):
        org = orgs[org_index]
        if len(mass_email_queries[query_index] + f"{org.email},") < 2000:
            mass_email_queries[query_index] += f"{org.email},"
            org_index += 1
        else:
            query_index += 1
            mass_email_queries.append(f"mailto:?bcc=")

    # if mass email queries is made of empty strings, set it to false
    if mass_email_queries[0] == "mailto:?bcc=":
        mass_email_queries = False

    context = {
        'mass_email_links': mass_email_queries,
        'count': len(mass_email_queries) if mass_email_queries else 0,
        'form': form
    }

    return render(request, 'app/mass_email.html', context)

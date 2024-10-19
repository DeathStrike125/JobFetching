import requests
import os
from requests.auth import HTTPBasicAuth
import csv
import xml.etree.ElementTree as ET

# Use environment variables for credentials
username = os.environ.get("ONET_USERNAME", "futurenex1")
password = os.environ.get("ONET_PASSWORD", "2264jfh")

# The O*NET API base URL
base_url = "https://services.onetcenter.org/ws/mnm/browse/48"

def fetch_jobs(url):
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        
        if 'xml' not in response.headers.get('Content-Type', ''):
            print(f"Unexpected content type: {response.headers.get('Content-Type')}")
            print(f"Response text: {response.text[:200]}...")
            return [], None

        # Parse XML
        root = ET.fromstring(response.content)
        
        # Extract careers
        careers = []
        for career in root.findall('.//career'):
            title = career.find('title').text if career.find('title') is not None else 'No title'
            code = career.find('code').text if career.find('code') is not None else 'No code'
            careers.append({'title': title, 'code': code})
        
        # Find the 'next' link
        next_link = root.find(".//link[@rel='next']")
        next_url = next_link.get('href') if next_link is not None else None

        return careers, next_url
    except requests.exceptions.RequestException as err:
        print(f"Error fetching data: {err}")
        return [], None

# Collect all jobs
all_jobs = []
current_url = base_url

while current_url:
    jobs, next_url = fetch_jobs(current_url)
    all_jobs.extend(jobs)
    current_url = next_url

# Output jobs to CSV
output_file = "onet_jobs.csv"
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['title', 'code'])
    writer.writeheader()
    for job in all_jobs:
        writer.writerow({'title': job.get('title', 'No title'), 'code': job.get('code', 'No code')})

print(f"Total jobs collected: {len(all_jobs)}")
print(f"Jobs have been written to {output_file}")

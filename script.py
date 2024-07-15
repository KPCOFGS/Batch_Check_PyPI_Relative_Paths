import requests
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urlparse, urljoin
from requests.exceptions import ConnectionError

def check_links(link_url):
    absolute_url = ""
    response = requests.get(link_url)
    if response.status_code != 200:
        print(f"Error: Failed to fetch {link_url}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    project_description = soup.find(class_="project-description")
    if project_description:
        links = project_description.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('mailto:'):
                continue
            elif href.startswith('http'):
                absolute_url = href
            else:
                absolute_url = urljoin(link_url, href)
            try:
                link_response = requests.head(absolute_url, allow_redirects=True)
            except ConnectionError as e:
                print(f"{link_url} ---> Connection error for link: {absolute_url} ")
                continue
            if link_response.status_code != 200:
                print(f"{link_url} ---> Bad link: {absolute_url} -- Status Code: {link_response.status_code}")
    else:
        print("No project description found on the page.")

# Parse command line arguments
parser = argparse.ArgumentParser(description='Get a specified number of pages from a URL.')
parser.add_argument('--pages', type=int, required=True, help='The number of pages to scrape.')
parser.add_argument('--starting-page', type=int, default=1, help='The starting page for scraping.')
args = parser.parse_args()
counter = args.starting_page
if counter < 1:
    raise ValueError("Starting page should be at least 1")
while counter <= args.pages + args.starting_page - 1:
    url = "https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3&o=-created&q=&page=" + str(counter)
    response = requests.get(url)

    # If the status code is 404, break the loop
    if response.status_code == 404:
        print("Page not found. Breaking the loop.")
        break

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the 'ul' element with the specified aria-label
    ul_element = soup.find('ul', {'aria-label': 'Search results'})

    # Get all 'a' elements (links) within the 'ul' element
    links = ul_element.find_all('a')

    # Print the URLs of the links and check them
    for link in links:
        result = "https://pypi.org" + link.get('href')
        check_links(result)

    counter += 1

from urllib import request as urlrequest
from bs4 import BeautifulSoup


def sort_(input_list):
    return sorted(input_list)


def scrape(url):
    print(f" Scraping URL for {url} ")
    html = urlrequest.urlopen(url).read()
    html[:60]
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find('title')
    print(f" The title is  {title} ")
    return title


def is_app_healthy():
    """
    """
    return True
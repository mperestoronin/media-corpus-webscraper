import requests
from bs4 import BeautifulSoup

def create_soup(url, header):
    """Загружает HTML страницы по URL."""
    response = requests.get(url, headers=header)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')
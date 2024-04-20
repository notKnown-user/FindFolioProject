import csv
import requests
from bs4 import BeautifulSoup

def search_linkedin(name, surname, location):
    search_url = f'https://www.linkedin.com/search/results/people/?keywords={name}+{surname}&origin=GLOBAL_SEARCH_HEADER&geoUrn=%5B{location}%5D'
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        profile_urls = []
        results = soup.find_all('li', class_='search-result')
        for result in results:
            profile_url = result.find('a', class_='search-result__result-link')['href']
            profile_urls.append(profile_url)
        return profile_urls
    else:
        print("Failed to fetch search results.")
        return []

def scrape_profile(profile_url):
    response = requests.get(profile_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        photo = soup.find('img', class_='pv-top-card__photo')['src']
        name = soup.find('li', class_='inline t-24 t-black t-normal break-words').text.strip()
        surname = soup.find('li', class_='inline t-24 t-black t-normal break-words').text.strip()
        location = soup.find('li', class_='t-16 t-black t-normal inline-block').text.strip()
        return {
            'photo': photo,
            'name': name,
            'surname': surname,
            'location': location
        }
    else:
        print("Failed to fetch profile page.")
        return {}

def write_to_csv(profiles, filename='linkedin_profiles.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['photo', 'name', 'surname', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)

def main():
    name = input("Enter the person's name: ")
    surname = input("Enter the person's surname: ")
    location = input("Enter the person's location: ")

    profile_urls = search_linkedin(name, surname, location)

    profiles = []
    for profile_url in profile_urls:
        profile_info = scrape_profile(profile_url)
        profiles.append(profile_info)

    write_to_csv(profiles)

if name == "main":
    main()

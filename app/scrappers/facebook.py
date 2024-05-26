from facebook_scraper import get_profile

def facebook_scraper(profile_url):
    username = profile_url.split('/')[-1]  # Extract username from profile URL
    profile = get_profile(username)
    return profile

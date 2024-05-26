from instaloader import Instaloader, Profile

def instagram_scraper(profile_url):
    loader = Instaloader()
    username = profile_url.split('/')[-1]  # Extract username from profile URL
    profile = Profile.from_username(loader.context, username)
    data = {
        "followers": profile.followers,
        "following": profile.followees,
        "posts": profile.mediacount
    }
    return data

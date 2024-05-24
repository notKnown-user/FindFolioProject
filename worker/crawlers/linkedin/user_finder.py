class LinkedInUserFinder:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    def get_access_token(self):
        auth_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        auth_params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }
        response = requests.post(auth_url, data=auth_params)
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            return self.access_token
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def search_users_by_skills(self, skills):
        if not self.access_token:
            print("Access token is not available. Please get the access token first.")
            return None

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        skills_query = ' OR '.join(skills)
        search_url = f'https://api.linkedin.com/v2/people/(skills:({skills_query}))'
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
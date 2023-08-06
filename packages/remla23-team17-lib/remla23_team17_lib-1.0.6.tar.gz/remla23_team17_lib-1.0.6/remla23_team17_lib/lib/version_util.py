import requests


class VersionUtil:
    def __init__(self, repo_id):
        self.repo_id = repo_id

    def get_version(self):
        api_url = f"https://api.github.com/repos/{self.repo_id}/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            release_data = response.json()
            version = release_data.get("tag_name")
            return version
        else:
            return "Unknown"

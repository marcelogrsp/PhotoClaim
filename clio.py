from datetime import datetime, timedelta
import requests
import dropbox
import time
import json

class Clio:
    # Credentials
    # It is strictly recommended to use environment variables instead of plain text
    API_BASE_URL = "eu.app.clio.com"
    CLIENT_ID = "client_id" # or os.environ.get('CLIO_CLIENT_ID')
    CLIENT_SECRET = "client_secret" # or os.environ.get('CLIO_CLIENT_SECRET')

    # Dropbox client
    ACCESS_TOKEN = 'access_token' # or os.environ.get('DROPBOX_ACCESS_TOKEN')
    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    def __init__(self):
        self.session = requests.Session()
        self.auth()

        assert f"http://{Clio.API_BASE_URL}/api/v4/users/who_am_i"

    def refresh_token(self):
        refresh_token = self.access_token.get("refresh_token")
        try:
            url = f"https://{Clio.API_BASE_URL}/oauth/token?grant_type=refresh_token&client_id={Clio.CLIENT_ID}&client_secret={Clio.CLIENT_SECRET}"

            payload=f'refresh_token={refresh_token}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)

            token = json.loads(response.text)
            
            if token.get("refresh_token") is None: token['refresh_token'] = refresh_token
            token['expires_at'] = (datetime.now() + timedelta(seconds=token.get('expires_in'))).timestamp()
            self.access_token = token
            Clio.dbx.files_upload(json.dumps(token).encode(), "/token.json", mode=dropbox.files.WriteMode.overwrite)

        except Exception as e:
            print(e)

    def get_matters(self, *fields, **filters):
        fields = ",".join(fields)

        params = {
            'fields': fields
        }
        
        # params.update(filters.get('filters'))

        url = f"https://{Clio.API_BASE_URL}/api/v4/matters?"
        
        matters = []
        for matter in self.fetch_data(url, params):
            assert matter
            matters.extend(matter)
            time.sleep(2)

        return matters
    
    def get_total_matters(self, *fields, **filters):
        fields = ",".join(fields)

        params = {
            'fields': fields
            
        }
        params.update(filters.get('filters'))

        url = f"https://{Clio.API_BASE_URL}/api/v4/matters"

        total_matters = self.session.get(url, params=params).json()['meta']['records']
        
        return total_matters

    def get_tasks(self):
        url = f"https://{Clio.API_BASE_URL}/api/v4/tasks"
        
        tasks = []
        for task in self.fetch_data(url):
            assert task
            tasks.extend(task)

        return tasks

    def fetch_data(self, url, params = {}):
        response = self.session.get(url, params=params).json()
        while response.get('meta').get('paging').get('next') is not None:
            response = self.session.get(url, params=params).json()
            data = response['data']
            url = response.get('meta').get('paging').get('next')
            yield data
        if url is not None: yield response['data']

    def auth(self):
        file_url = Clio.dbx.files_get_temporary_link('/token.json').link
        access_token = requests.get(file_url).text

        self.access_token = json.loads(access_token)

        if self.access_token.get("expires_at") < datetime.now().timestamp(): self.refresh_token()

        self.session.headers = {'Authorization': 'Bearer ' + self.access_token.get("access_token")}

import requests, json

host = "eu.app.clio.com"

authorize_url = f"https://{host}/oauth/authorize"
token_url = f"https://{host}/oauth/token"
callback_uri = "http://127.0.0.1"
test_api_url = f"https://{host}/api/v4/users/who_am_i"

# Credentials
# It is strictly recommended to use environment variables instead of plain text
client_id = "client_id" # or os.environ.get('CLIO_CLIENT_ID')
client_secret = "client_secret" # or os.environ.get('CLIO_CLIENT_SECRET')

authorization_redirect_url = authorize_url + '?response_type=code&client_id=' + client_id + '&redirect_uri=' + callback_uri

print("go to the following url on the browser and enter the code from the returned url: ")
print("---  " + authorization_redirect_url + "  ---")

authorization_code = input('code: ')

"""
client_id:     application key from above
client_secret: application secret from above
grant_type:    "authorization_code"
code:          Authorization code from the redirect above
redirect_uri:  Redirect URI used in the authorization request above
"""

data = {'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': callback_uri}

print("requesting access token")

access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False, auth=(client_id, client_secret))

print("response")
print(access_token_response.headers)
print('body: ' + access_token_response.text)

# we can now use the access_token as much as we want to access protected resources.
tokens = json.loads(access_token_response.text)
access_token = tokens['access_token']
print("access token: " + access_token)

api_call_headers = {'Authorization': 'Bearer ' + access_token}
api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)

print(api_call_response.text)

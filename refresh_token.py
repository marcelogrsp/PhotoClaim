from datetime import datetime, timedelta
import requests
import json
import os

def lambda_handler(event, context):
    host = "eu.app.clio.com"
    refresh_token = open("token.json", "r")
    refresh_token = json.load(refresh_token).get("refresh_token")
    try:
        # Credentials
        # It is strictly recommended to use environment variables instead of plain text
        client_id = "client_id" # or os.environ.get('CLIO_CLIENT_ID')
        client_secret = "client_secret" # or os.environ.get('CLIO_CLIENT_SECRET')

        url = f"https://{host}/oauth/token?grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}"

        payload=f'refresh_token={refresh_token}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

        token = json.loads(response.text)
        if token.get("refresh_token") is None: token['refresh_token'] = refresh_token
        token_json = open("token.json", "w")
        json.dump(token, token_json)

        os.environ['CLIO_ACCESS_TOKEN'] = token['access_token']
        os.environ['CLIO_REFRESH_TOKEN'] = token['refresh_token']
        os.environ['CLIO_ACCESS_TOKEN_EXPIRATION'] = (datetime.now() + timedelta(seconds=token.get('expires_in'))).timestamp()

    except requests.RequestException as e:
        print(e)
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            "location": response.text
        }),
    }

lambda_handler(None, None)

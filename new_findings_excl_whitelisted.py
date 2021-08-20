import pandas as pd
import requests
import datetime
import dropbox
import io

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def session():
    session = requests.session()
    token = login()

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.photoclaim.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "api.photoclaim.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en-gb",
        "Connection": "keep-alive"
    }
    session.headers = headers
    return session

def login():    
    url = "https://api.photoclaim.com/auth/login"

    payload = {
        "email": "email",
        "password": "password"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.photoclaim.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "api.photoclaim.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Content-Length": "65",
        "Accept-Language": "en-gb",
        "Connection": "keep-alive",
        "Authorization": "Basic Og=="
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()['token']

def matters(created_at_start, created_at_end):
    params = {
        "desc": "1",
        "per_page": "25",
        "first_found_from": f"{created_at_start} 00:00:00",
        "first_found_to": f"{created_at_end} 23:59:59",
        "page": "1",
        "with_whitelisted": "0"
    }
    matters = session.get('https://api.photoclaim.com/matches', params=params)
    total = matters.json()['total']
    return total


if __name__ == "__main__":
    ACCESS_TOKEN = 'access_token' # or os.environ.get('DROPBOX_ACCESS_TOKEN')
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    
    file_url = dbx.files_get_temporary_link('/new_findings_excl_whitelisted.csv').link

    df = pd.read_csv(file_url)

    session = session()

    cur_month = datetime.datetime.today().month
    cur_year = datetime.datetime.today().year

    created_at_start = datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d')
    created_at_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')
    matters_total = matters(created_at_start, created_at_end)

    df.drop(df.loc[df['period'] == created_at_start].index, inplace=True)

    df = df.append({"period": created_at_start , "total": matters_total}, ignore_index=True)

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    print(df)
    
    data = dbx.files_upload(stream.getvalue().encode(), "/new_findings_excl_whitelisted.csv", mode=dropbox.files.WriteMode.overwrite)

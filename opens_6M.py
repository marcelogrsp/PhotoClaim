from clio import Clio
import pandas as pd
import datetime
import dropbox
import io

clio = Clio()

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


if __name__ == "__main__":
    ACCESS_TOKEN = 'access_token' # or os.environ.get('DROPBOX_ACCESS_TOKEN')

    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    file_url = dbx.files_get_temporary_link('/opens_6M.csv').link

    df = pd.read_csv(file_url)


for i in range(8,13):
    cur_year = datetime.datetime.today().year - 2
    cur_month = i

    # cur_month = datetime.datetime.today().month
    # cur_year = datetime.datetime.today().year

    # cur_month = 1
    # cur_year = 2020

    # Open 6M
    open_date_start = (datetime.date(cur_year, cur_month, 1) + datetime.timedelta(-5*365/12)).strftime('%Y-%m-%d')
    open_date_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')

    total_matters = clio.get_total_matters('id','etag','open_date','created_at','status', filters={'open_date[]': [f">={open_date_start}", f"<={open_date_end}"]})
    
    df.drop(df.loc[df['period'] == datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d')].index, inplace=True)

    df = df.append({"period": datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d') , "total": total_matters}, ignore_index=True)

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    data = dbx.files_upload(stream.getvalue().encode(), "/opens_6M.csv", mode=dropbox.files.WriteMode.overwrite)

    print(df)
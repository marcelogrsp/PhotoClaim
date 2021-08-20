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

    for i in range(1,9):

        file_url = dbx.files_get_temporary_link('/pending_3m.csv').link

        df = pd.read_csv(file_url)

        cur_month = datetime.datetime.today().month
        cur_year = datetime.datetime.today().year

        cur_year = datetime.datetime.today().year
        cur_month = i

        # Pending 3M
        pending_date_start = (datetime.date(cur_year, cur_month, 1) + datetime.timedelta(-2*365/12)).strftime('%Y-%m-%d')
        pending_date_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')

        total_matters = clio.get_total_matters('id','etag','pending_date','created_at','status', filters={'pending_date[]': [f">={pending_date_start}", f"<={pending_date_end}"]})
        
        df.drop(df.loc[df['period'] == datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d')].index, inplace=True)

        df = df.append({"period": datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d') , "total": total_matters}, ignore_index=True)

        stream = io.StringIO()
        df.to_csv(stream, index=False)

        print(df)

        data = dbx.files_upload(stream.getvalue().encode(), "/pending_3m.csv", mode=dropbox.files.WriteMode.overwrite)

        # Close 3M
        file_url = dbx.files_get_temporary_link('/close_3m.csv').link

        df = pd.read_csv(file_url)

        close_date_start = (datetime.date(cur_year, cur_month, 1) + datetime.timedelta(-2*365/12)).strftime('%Y-%m-%d')
        close_date_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')

        total_matters = clio.get_total_matters('id','etag','close_date','created_at','status', filters={'close_date[]': [f">={close_date_start}", f"<={close_date_end}"], "custom_field_values[54517]": '28842'})
        
        df.drop(df.loc[df['period'] == datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d')].index, inplace=True)

        df = df.append({"period": datetime.date(cur_year, cur_month, 1).strftime('%Y-%m-%d') , "total": total_matters}, ignore_index=True)

        stream = io.StringIO()
        df.to_csv(stream, index=False)

        print(df)
        
        data = dbx.files_upload(stream.getvalue().encode(), "/close_3m.csv", mode=dropbox.files.WriteMode.overwrite)

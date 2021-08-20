from dateutil.relativedelta import relativedelta
import pandas as pd
import pymysql
import datetime
import dropbox
import io

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


if __name__ == "__main__":
    # Credentials
    # It is strictly recommended to use environment variables instead of plain text

    host = "host" # or os.environ.get('DB_HOST')
    port = "port" # or os.environ.get('DB_PORT')
    db = "db" # or os.environ.get('DB_DB')
    user = "user" # or os.environ.get('DB_USER')
    password = "password" # or os.environ.get('DB_PASSWORD')

    conn = pymysql.connect(host=host,port=port,db=db,user=user,password=password)

    ACCESS_TOKEN = 'access_token' # or os.environ.get('DROPBOX_ACCESS_TOKEN')

    dbx = dropbox.Dropbox(ACCESS_TOKEN)

    file_url = dbx.files_get_temporary_link('/processed_6M.csv').link

    df = pd.read_csv(file_url)

    cur_month = datetime.datetime.today().month
    cur_year = datetime.datetime.today().year

    # cur_month = 1
    # cur_year = 2020

    created_at_start = (datetime.date(cur_year, cur_month, 1) + relativedelta(months=-5)).strftime('%Y-%m-%d')
    created_at_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')

    sql = f"""
        SELECT
            DATE_FORMAT(created_at, "%e/%m/%Y") as period,
            JSON_EXTRACT(data, "$[*].new_values.category_id") AS target_category
        FROM
            logs
        WHERE
            ACTION = 'matches updated'
            AND created_at >= '{created_at_start}'
            AND created_at <= '{created_at_end}'
            and(JSON_EXTRACT(data, "$[*].new_values.category_id")
                LIKE '%5%'
                OR JSON_EXTRACT(data, "$[*].new_values.category_id")
                LIKE '%4%')
    """

    df_1 = pd.read_sql(sql, conn)

    for i in range(len(df_1)):
        df_1['target_category'].values[i] = len(df_1['target_category'].values[i].split(","))

    print(df_1.columns)
    print(df_1['target_category'])

    processed = df_1['target_category'].sum()

    print(df_1)

    df.drop(df.loc[df['period'] == datetime.date(cur_year, cur_month, 1).strftime('%d/%m/%Y')].index, inplace=True)
    df = df.append({"period": datetime.date(cur_year, cur_month, 1).strftime('%d/%m/%Y') , "total": processed}, ignore_index=True)

    print(df)
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    data = dbx.files_upload(stream.getvalue().encode(), "/processed_6M.csv", mode=dropbox.files.WriteMode.overwrite)
    
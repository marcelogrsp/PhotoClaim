# Klipfolio Sales Pipeline Dashboard

## How to update data
The data used in Klipfolio is extracted by a Python script running in AWS Lambda.

![Lambda Functions](https://quantryx.s3.eu-west-2.amazonaws.com/lambda_functions.png "Lambda Functions")

The scripts run every day at 02:00AM GMT. The scheduler can be found at Amazon EventBridge

![Amazon EventBridge](https://quantryx.s3.eu-west-2.amazonaws.com/amazon_eventbridge.png "Amazon EventBridge")

### What it does

The scripts fetches data inside a date range, determined in each by two variables `xpto_date_start` and `xpto_date_end`:

For example in **opens_6M** function we see the two variables `open_date_start` and `open_date_end` that determine the period for the last 6 months.
The reference is ALWAYS the current year and month, although, if you want to fetch past data you can change the variables `cur_month` and `cur_year` to the desired ones.

```python
# Open 6M
open_date_start = (datetime.date(cur_year, cur_month, 1) + datetime.timedelta(-5*365/12)).strftime('%Y-%m-%d')
open_date_end = last_day_of_month(datetime.date(cur_year, cur_month, 1)).strftime('%Y-%m-%d')
```

```python
cur_month = datetime.datetime.today().month
cur_year = datetime.datetime.today().year
```

**Example**

If you want to get data of total matters opened in the last 6 monhts at March 2018 you can to it simply assigning:

```python
cur_month = 3
cur_year = 2018
```

And call the function clicking on `TEST`.

![Test](https://quantryx.s3.eu-west-2.amazonaws.com/test.png "Test")

### Where the output is stored

The output is stored on PhotoClaim's Dropbox at https://www.dropbox.com/sh/2f9kc6fxeqaub57/AAAlepd1ERZX10rXXnvYy4eGa?dl=0

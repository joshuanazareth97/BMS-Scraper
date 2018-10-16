from flask import Flask, render_template, request
import urllib.request
from bs4 import BeautifulSoup as bs
import datetime

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("homepage.html")

@app.route("/generate_csv", methods=["POST","GET"])
def generate_csv():
    print(request.form.get("city","all"))

    #list of dates to check as filter, remains empty (1) by default; (2) in case of "all" filter; (3) in case of error
    date_range = []
    date_filter = request.form.get("date")
    curr_day = datetime.datetime.now().weekday()
    print(curr_day)
    if date_filter == "today":
        date_range.append(datetime.datetime.now())
    elif date_filter == "tomorrow":
        date_range.append(datetime.datetime.now()+datetime.timedelta(days=1))
    elif date_filter == "next":
        date_range = [datetime.datetime.now()+datetime.timedelta(days=12-curr_day),
            datetime.datetime.now()+datetime.timedelta(days=13-curr_day)]
    elif date_filter == "this":
        #handling usual cases, searching for this weekend on a weekday
        if curr_day < 5:
            date_range = [datetime.datetime.now()+datetime.timedelta(days=5-curr_day),
                datetime.datetime.now()+datetime.timedelta(days=6-curr_day)]
        #handling edge case where this weekend filter chosen on saturday
        elif curr_day == 5:
            date_range = [datetime.datetime.now().strftime("%Y%m%d"),
                datetime.datetime.now()+datetime.timedelta(days=1)]
        elif curr_day == 6:
            date_range.append(datetime.datetime.now())
    print(date_range)

    #NOTE: hardcoded mumbai as default city
    with urllib.request.urlopen("https://in.bookmyshow.com/{}/events".format(request.form.get("city","mumbai"))) as bms:
        webpage_html = bms.read()

    webpage_parsed = bs(webpage_html, "html.parser")

    event_tags = webpage_parsed.find_all(lambda x: str(x.name) == "aside" and str(x.get("id")).startswith("eventCards"))
    for event in event_tags:
        #building list of datetime objects
        date_strings = event["data-datecode-filter"].split('|')
        if date_strings[-1] is "": date_strings = date_strings[:-1] #removes last element of date list (usually empty string)
        dates = [datetime.datetime.strptime(string,"%Y%m%d").date() for string in date_strings]
        # print(dates)
        if date_range and all(day.date() not in dates for day in date_range):
            # print("Skipping")
            continue

        title = event.find("h4").string
        price = event["data-price-filter"]
        print(title, price, dates[0])
        # print(title,price)
        # print(dates_list)
        # # print(event.a.get("onclick"))
        # print()
    return "Success"

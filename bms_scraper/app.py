from flask import Flask, render_template, request, send_file
import urllib.request
from bs4 import BeautifulSoup as bs
import datetime
import csv

from io import StringIO, BytesIO

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("homepage.html")

@app.route("/generate_csv", methods=["POST","GET"])
def generate_csv():
    print(request.form.get("city","all"))

    #NOTE: hardcoded mumbai as default city
    city_filter = request.form.get("city","mumbai")
    #list of dates to check as filter, remains empty (1) by default; (2) in case of "all" filter; (3) in case of error
    date_range = []
    date_filter = request.form.get("date")
    curr_day = datetime.datetime.now().weekday()


    #creating date filter list
    if date_filter == "today":
        date_range.append(datetime.datetime.now())
    elif date_filter == "tomorrow":
        date_range.append(datetime.datetime.now()+datetime.timedelta(days=1))
    elif date_filter == "nextweekend":
        date_range = [datetime.datetime.now()+datetime.timedelta(days=12-curr_day),
            datetime.datetime.now()+datetime.timedelta(days=13-curr_day)]
    elif date_filter == "thisweekend":
        #handling usual cases, searching for this weekend on a weekday
        if curr_day < 5:
            date_range = [datetime.datetime.now()+datetime.timedelta(days=5-curr_day),
                datetime.datetime.now()+datetime.timedelta(days=6-curr_day)]
        #handling edge case where this weekend filter chosen on saturday
        elif curr_day == 5:
            date_range = [datetime.datetime.now(),
                datetime.datetime.now()+datetime.timedelta(days=1)]
        #handling edge case where this weekend filter chosen on sunday
        elif curr_day == 6:
            date_range.append(datetime.datetime.now())

    with urllib.request.urlopen("https://in.bookmyshow.com/{}/events".format(city_filter)) as bms:
        webpage_html = bms.read()

    webpage_parsed = bs(webpage_html, "html.parser")

    event_tags = webpage_parsed.find_all(lambda x: str(x.name) == "aside" and str(x.get("id")).startswith("eventCards"))

    #building final list of events
    filtered_events = [["Title","Price","Date"]]
    for event in event_tags:
        #building list of datetime objects
        date_strings = event["data-datecode-filter"].split('|')
        if date_strings[-1] is "": date_strings = date_strings[:-1] #removes last element of date list (usually empty string)
        dates = [datetime.datetime.strptime(string,"%Y%m%d").date() for string in date_strings]

        #Skip current event if filter present and it doesn't meet criteria
        if date_range and all(day.date() not in dates for day in date_range): continue

        #get title and price
        title = str(event.find("h4").text)

        price = event["data-price-filter"]

        #append title, price and formatted datetime to list if filter criteria matched
        filtered_events.append([title,price,dates[0].strftime("%d-%b-%Y")])

    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerows(filtered_events)

    buffer = BytesIO()
    buffer.write(csv_file.getvalue().encode('utf-8'))
    buffer.seek(0)
    csv_file.close()
    return send_file(buffer, as_attachment=True,
        attachment_filename='events_{}_{}.csv'.format(city_filter,date_filter),
        mimetype='text/csv')

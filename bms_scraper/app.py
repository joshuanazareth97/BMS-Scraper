from flask import Flask, render_template, request
import urllib.request
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

@app.route("/")
def root():
    return render_template("homepage.html")

@app.route("/generate_csv", methods=["POST","GET"])
def generate_csv():
    print(request.form.get("city","all"))

    #NOTE: hardcoded mumbai as default city
    with urllib.request.urlopen("https://in.bookmyshow.com/{}/events".format(request.form.get("city","mumbai"))) as bms:
        webpage_html = bms.read()

    webpage_parsed = bs(webpage_html, "html.parser")

    #building list of event tags
    event_tags = webpage_parsed.find_all(lambda x: str(x.name) == "aside" and str(x.get("id")).startswith("eventCards"))
    for event in event_tags:
        title = event.find("h4").string
        print(title)
        try:
            print(event["data-datecode-filter"].split('|'))
        except AttributeError:
            print("None")
        print(event["data-price-filter"])
        # print(event.a.get("onclick"))
        print()
    return "Success"

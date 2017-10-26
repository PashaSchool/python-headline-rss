import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib


app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
			'cnn': 'http://rss.cnn.com/rss/edition.rss',
			'fox': 'http://feeds.foxnews.com/foxnews/latest',
			'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
			'city': 'London,UK',
			'currency_from':'GBP',
			'currency_to':'USD'}

CURRENCY_URL ="https://openexchangerates.org//api/latest.json?app_id=47131325c99b43d6a60380f1dc2f0642"

@app.route("/", methods=["GET", "POST"])
def home():
	# get customized headlines, based on user input or default
	publication = request.form.get('publication')
	if not publication:
		publication = DEFAULTS['publication']

	articles = get_news(publication)
	# get customized weather based on user input or default
	city = request.args.get('city')
	if not city:
		city = DEFAULTS['city']
	weather = get_wether(city)

	currency_from = request.args.get("currency_from")

	if not currency_from:
		currency_from = DEFAULTS["currency_from"]

	currency_to = request.args.get('currency_to')
	if not currency_to:
		currency_to = DEFAULTS['currency_to']

	rate = get_rate(currency_from, currency_to)


	return render_template("home.html",
		articles=articles,
		weather=weather,
		currency_from=currency_from,
		currency_to=currency_to,
		rate=rate)


def get_rate(frm, to):
	all_currancy = urllib.request.urlopen(CURRENCY_URL).read()

	parsed = json.loads(all_currancy).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())

	return to_rate/frm_rate


def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication=DEFAULTS['publication']
	else:
		publication=query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']
	


def get_wether(query):
	api_url="http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cda220bfa0904411b6a1be1f8826d77d"

	query = urllib.parse.quote(query)
	url = api_url.format(query)

	data = urllib.request.urlopen(url).read()
	parsed = json.loads(data)
	weather = None

	if parsed.get("weather"):
		weather = {
		"description" : parsed["weather"][0]["description"],
		"temperature" : parsed["main"]["temp"],
		"city" : parsed["name"],
		"country" : parsed["sys"]["country"]
		}

	return weather

if __name__ == '__main__':
	app.run(port=5001, debug=True)
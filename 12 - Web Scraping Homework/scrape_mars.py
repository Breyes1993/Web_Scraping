from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless=False)


def scrape():
    final_data = {}
    output = marsnews()
    final_data["Mars_News"] = output[0]
    final_data["Mars_Paragraph"] = output[1]
    final_data["Mars_Image"] = marsimage()
    final_data["Mars_Weather"] = marsweather()
    final_data["Mars_Facts"] = marsfacts()
    final_data["Mars_Hemisphere"] = marshemisphere()
    return final_data

# NASA Mars News
def marsnews():
    MarsNews_url = "https://mars.nasa.gov/news/"
    browser.visit(MarsNews_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_='list_text')
    news_title = article.find("div", class_="content_title").text
    news_p = article.find("div", class_ ="article_teaser_body").text
    output = [news_title, news_p]
    return output
    
    
# JPL Mars Space Images
def marsimage():   
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    image = soup.find("img", class_="thumb")["src"]
    featured_image_url = "https://www.jpl.nasa.gov" + image
    return featured_image_url
      
    
# Mars Weather
def marsweather():
    url_weather = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_weather)   
    html_weather = browser.html
    soup = BeautifulSoup(html_weather, "html.parser")
    mars_weather = soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    return mars_weather


# Mars Facts
def marsfacts():
    Mars_facts_url = "https://space-facts.com/mars/"
    Mars_details = pd.read_html(Mars_facts_url) 
    Mars_details[0].columns = ["Traits", "Details"]
    Mars_details[0].set_index(["Traits"])    
    browser.visit(Mars_facts_url)
    Marsplanet_data = pd.read_html(Mars_facts_url)
    Marsplanet_data = pd.DataFrame(Marsplanet_data[0])
    Mars_facts = Marsplanet_data.to_html(header = True, index = True)
    
    
# Mars Hemispheres
def marshemisphere():
    hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemispheres_url)
    Mars_hemisph = []
    products = BeautifulSoup(browser.html, "html.parser").find("div", class_ = "result-list" )
    hemispheres = products.find_all("div", class_="item")
    for hemisphere in hemispheres:
        url_title = hemisphere.find("h3").text
        edited_title = url_title.replace("Enhanced", "")
        image_link = "https://astrogeology.usgs.gov/" + hemisphere.find("a")["href"]    
        browser.visit(image_link)
        image_url = BeautifulSoup(browser.html, "html.parser").find("div",class_="downloads").find("a")["href"]
        Mars_hemisph.append({"title": edited_title, "img_url": image_url})
    return Mars_hemisph
    
#-----------------------------------------------------------------------------------------------------------#

app = Flask(__name__)

mongo = PyMongo(app)

@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars = mars)

@app.route("/scrape")
def scrape():
    mars = mongo.db.mars 
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    return redirect("http://localhost:5000/", code=302)


if __name__ == "__main__":
    app.run(debug=True)


import os
import time
import calendar
from functools import partial

import pandas as pd
import numpy as np
from selenium import webdriver

timestamp = calendar.timegm(time.gmtime())

# Configuration for the script
########################################################################################
# NOTE: Do not edit anything other than this block of script
# NOTE: To Set eny of the below values to default set it to False

WORK_DIR = os.path.abspath('.')  # Sets the working directory

CHROME_PATH = False  # ChromeDriver Path (Default: $WORK_DIR/chromedriver)

IN_PATH = False  # Input File Path (Default: $WORK_DIR/google_locations.csv)
PLACE_ID_COL = False  # URL column of the input file (Default: place_id)

# Output File Path (Default: $WORK_DIR/google_reviews_<TIMESTAMP>.csv)
OUT_PATH = False

# If you wish real time persistance with a mongodb external database set the bellow
MONGO_URL = "mongodb://stax_user:stax_pwd@127.0.0.1:27017/urgent_care?authSource=admin"
# mongodb://<username>:<password>@<host>:<port>/<default_DB>?authSource=admin"

# Defaults to : google_reviews_<TIMESTAMP>
MONGO_COLLECTION = 'competitors_reviews' 
########################################################################################


# Fetch information from a single block of review
########################################################################################
def fetch_block_detail(url, block):
    try:
        user = block.find_element_by_class_name('section-review-title').text
    except:
        user = np.nan

    try:
        ratings = block.find_element_by_class_name(
            'section-review-stars').get_attribute('aria-label')
    except:
        ratings = np.nan

    try:
        date = block.find_element_by_class_name(
            'section-review-publish-date').text
    except:
        date = np.nan

    try:
        more = block.find_element_by_class_name(
            'section-expand-review').click()
        time.sleep(1)
    except:
        pass

    try:
        review = block.find_element_by_class_name('section-review-text').text
    except:
        review = np.nan

    d = {
        'user': user,
        'ratings': ratings,
        'date': date,
        'review': review,
        'url': url
    }

    if MONGO_URL:
        if MONGO_COLLECTION:
            col_name = MONGO_COLLECTION
        else:
            col_name = 'google_reviews_{}'.format(timestamp)
        try:
            from pymongo import MongoClient
            db = MongoClient(MONGO_URL).get_database()
            store = db[col_name]

            store.insert_one(d)
        except:
            print('Failed to perisit')

    return d
########################################################################################


# Open the URL,  do all interactions, extract blocks, run block info fetcher for every block
########################################################################################
def fetch_url_info(place_id):
    try:
        url = "https://www.google.com/maps/search/?api=1&query=Google&query_place_id={}".format(place_id)

        # Fetch the URL and wait for a sec
        driver.get(url)
        time.sleep(2)

        pane = driver.find_element_by_class_name('widget-pane-link')

        # Click the link and wat for a sec
        pane.click()
        time.sleep(2)

        # Fetch the initial number of links
        blocks = driver.find_elements_by_class_name('section-review-content')
        previous_reviews_count = len(blocks)
        last_review_count = previous_reviews_count + 1

        # Scroll down to the bottom
        while previous_reviews_count != last_review_count:
            previous_reviews_count = last_review_count
            # Scroll Down
            driver.execute_script(
                "var pane =document.querySelector('#pane > div > div.widget-pane-content.scrollable-y > div > div > div.section-listbox.section-scrollbox.scrollable-y.scrollable-show'); \
                pane.scroll(0, pane.scrollHeight); \
                ")
            time.sleep(2)
            blocks = driver.find_elements_by_class_name(
                'section-review-content')
            last_review_count = len(blocks)

        # If there is any review blocks found fetch the data
        fetch_block_detail_partial = partial(fetch_block_detail, url)
        if len(blocks):
            data = [fetch_block_detail_partial(block) for block in blocks]

            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print("Failed to fetch {}".format(url))
        print("Reason: {}\n".format(e))
        return pd.DataFrame()
########################################################################################


#  Setup Initial Variables
########################################################################################
if CHROME_PATH:
    chrome_path = CHROME_PATH
else:
    chrome_path = os.path.join(WORK_DIR, 'chromedriver')

driver = webdriver.Chrome(chrome_path)

if IN_PATH:
    df = pd.read_csv(IN_PATH)
else:
    df = pd.read_csv(os.path.join(WORK_DIR, 'google_locations.csv'))

if OUT_PATH:
    out_path = OUT_PATH
else:
    out_path = os.path.join(
        WORK_DIR, 'google_reviews_{}.csv'.format(timestamp))

if PLACE_ID_COL:
    place_id_col = PLACE_ID_COL
else:
    place_id_col = 'place_id'
########################################################################################


# Run Fetch Script
########################################################################################
data = df[place_id_col].map(fetch_url_info)
########################################################################################

# Save file
########################################################################################
pd.concat(list(data)).to_csv(out_path)
########################################################################################


# Close the Webdriver
########################################################################################
driver.close()
########################################################################################

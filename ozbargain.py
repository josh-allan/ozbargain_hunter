#!/usr/bin/env python

import os
import time
import requests

import feedparser
from dotenv import load_dotenv

load_dotenv()


feed = ["https://www.ozbargain.com.au/feed"]
interesting_searches = ['Samsung', 'Nvidia','PS5', 'Credit Card', 'Sony', 'nuc']

last_updated = None
matched_ids = []

#telegram bot token for API
bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

def search_feed(feed_url,
                interesting_searches,
                last_updated,
                matched_ids):
    '''Parse and process RSS feed(s) and return unique matched strings, published time and new matching entries, otherwise return none
    '''
    feed = feedparser.parse(feed_url)

    matching_entries = []
    new_matched_ids = []

    for entry in feed.entries:
        #Skip over entries that were published before the last entry that was processed
        if last_updated and entry.published_parsed <= last_updated:
            continue

        # We also want to skip over entries that have already been matched
        if matched_ids and entry.id in matched_ids:
            continue

        # If we match on a new string, lets append it to the appropriate list
        # ensuring to only alert on a new entry
        if any(term in entry.title or term in entry.description for term in interesting_searches):
            matching_entries.append(entry)
            new_matched_ids.append(entry.id)

    #Return the matching entries, the published time of the last entry
    #and the IDs of the new matching entries
    return matching_entries, feed.entries[-1].published_parsed if feed.entries else None, new_matched_ids

while True:
    matching_entries, last_updated, new_matched_ids = search_feed(feed[0],
                                                                  interesting_searches,
                                                                  last_updated,
                                                                  matched_ids)
    if matching_entries:
        for entry in matching_entries:
            print(f"Matching entry found in {feed[0]}: {entry.title}")
            # Notify via telegram API:
            message = f"A new matching entry was found in {feed[0]}: {entry.title}\n{entry.link}"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
            response = requests.get(url)
            if response.status_code == 200:
                print(f"\r\nTelegram message sent successfully.")
            else:
                print(f"Failed to send Telegram message. Status code: {response.status_code}")
    else:
        print(f"No new matching entries found in {feed[0]}.")

    matched_ids += new_matched_ids #Add the new matched IDs to the matched IDs list
    time.sleep(60) #Wait 60 seconds for the next run

#!/usr/bin/python

import requests
import json
import re
import mechanize
import cookielib
import sys
from BeautifulSoup import BeautifulSoup


# Variables
engaged = False
#topic_url="https://www.kvraudio.com/forum/viewtopic.php?f=1&t=470835"
topic_url = "http://www.kvraudio.com/forum/viewtopic.php?f=1&t=492028"
#topic_post_url = "https://www.kvraudio.com/forum/posting.php?mode=reply&f=1&t=470835"
topic_post_url = "https://www.kvraudio.com/forum/posting.php?mode=reply&f=1&t=492028"
# replace topic t= with current topic
topic_search_url = "https://www.kvraudio.com/forum/search.php?keywords=XXXXXXXX&t=492028&sf=msgonly"
login_url = "https://www.kvraudio.com/forum/ucp.php?mode=login"

username = "planetw"
password = "XYZ"

# max amount to bid for all software packages
total_max_bid = 600

software = {
    "Twolegs Bundle": {
        "search": "twolegs%20bundle",
        "amount": 5,
        "regex": re.compile('Twolegs.+Bundle.*?\$+.+([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 15,
        "bids": [],  #("bidderuser", int)
    },
    "TimeWARP2600": {
        "search": "timewarp2600",
        "amount": 5,
        "regex": re.compile('Time\s?Warp2600.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 60,
        "bids": [],  #("bidderuser", int)
    },
    "VSTBuzz 300 voucher": {
        "search": "VSTBuzz%20voucher",
        "amount": 1,
        "regex": re.compile('VSTBuzz.*?voucher.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 250,
        "bids": [],  #("bidderuser", int)
    },
    "Scaler plugin": {
        "search": "scaler%20plugin",
        "amount": 1,
        "regex": re.compile('Scaler.+plugin.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 10,
        "bids": [],  #("bidderuser", int)
    },
    # "Addictive Drums 2 Custom": {
    #     "search": "addictive%20drums%20custom",
    #     "amount": 1,
    #     "regex": re.compile('Addictive.*?Drums.*?2.*?Custom.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
    #     "max_bid": 1,
    #     "bids": [],  #("bidderuser", int)
    # },
    "Reaper Commercial License": {
        "search": "reaper%20commercial%20license",
        "amount": 2,
        "regex": re.compile('reaper.+commercial.+license.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 60,
        "bids": [],  #("bidderuser", int)
    },
    # "Melodyne 4 Studio License": {
    #     "search": "melodyne%204%20license",
    #     "amount": 1,
    #     "regex": re.compile('Melodyne.*?4.*?Studio.*?License.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
    #     "max_bid": 1,
    #     "bids": [],  #("bidderuser", int)
    # },
    # "Synth Magic Bundle 5": {
    #     "search": "synth%20magic%205",
    #     "amount": 5,
    #     "regex": re.compile('Synth.*?Magic.*?Bundle.*?5*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
    #     "max_bid": 60,
    #     "bids": [],  #("bidderuser", int)
    # },
    # "Studio Session Pack": {
    #     "search": "studio%20session%20pack",
    #     "amount": 3,
    #     "regex": re.compile('Studio.*?Session.*?Pack.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
    #     "max_bid": 1,
    #     "bids": [],  #("bidderuser", int)
    # },
    "TAL Coupon": {
        "search": "tal%20coupon",
        "amount": 5,
        "regex": re.compile('TAL.*?Coupon.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 100,
        "bids": [],  #("bidderuser", int)
    },
    "PSP EffectPack": {
        "search": "PSP%20Effect%20Pack",
        "amount": 1,
        "regex": re.compile('PSP.*?Effect.*?Pack.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 150,
        "bids": [],  #("bidderuser", int)
    },
    "MPowerSynth": {
        "search": "mpowersynth",
        "amount": 1,
        "regex": re.compile('Power.*?Synth.*?([1-9][0-9]*[0,5])', flags=re.IGNORECASE),
        "max_bid": 80,
        "bids": [],  #("bidderuser", int)
    }
}

total_bid_sum = 0


def login(username, password):

    # use mechanize ...
    
    # Browser
    br = mechanize.Browser()
    
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    
    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(False)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    
    br.addheaders = [('User-agent', 'Chrome')]
    
    # The site we will navigate into, handling it's session
    br.open(login_url)
    
    # View available forms
    #for f in br.forms():
    #    print f
        
    # Select the first (index zero) form
    br.select_form(nr=0)
        
    # User credentials
    br.form['username'] = username
    br.form['password'] = password
    # Login
    br.submit()

    return br



def search_software(browser,software_name):

    sw = software[software_name]
    print "searching for", software_name
    # make a single request to the homepage
    response = browser.open(topic_search_url.replace("XXXXXXXX", sw["search"])).read()
    # make soup
    soup = BeautifulSoup(response)
    
    #all posts without the initial auction post
    posts = soup.findAll("div",{"class": "inner"})[:-1]
    #posts_content = posts.findAll("div",{"class": "content"})
    
    for post in posts:
        re_software = re.compile(sw["regex"])
        #post_content_soup = BeautifulSoup(post)
        post_content = post.findAll("div",{"class": "content"})
        if not post_content:
            print "WARNING: no post content found something wrong?!, skipping software"
            return
        latest_bid = re_software.findall(post_content.text)
        if latest_bid:
            latest_bid = latest_bid[0]
            latest_bid_user_soup = post.findAll("dt",{"class": "author"})[0]
            latest_bid_user = latest_bid_user_soup.text.strip("by")
            # exclude initial post by admin
            if latest_bid_user != "Luftrum":
                print "Found bid from user", latest_bid_user, "$", latest_bid, "for", software_name
                bid = (latest_bid_user, int(latest_bid))
        
                software[software_name]["bids"].append(bid)
                software[software_name]["bids"].sort(key=lambda x: x[1])

                
def bid_software(browser,software_name):

    search_software(browser, software_name)

    global total_bid_sum
    
    amount = software[software_name]["amount"]
    max_bid = software[software_name]["max_bid"]
    software_bids = software[software_name]["bids"]
    relevant_bids = software_bids[:amount]
    print "found the last relevant bids", relevant_bids

    # dont overbid ourselfes
    if [ bid for bid in relevant_bids if bid[0] == username]:
        print "not bidding. we would overbid ourselve"
    else:
        # only overbid the lowest bid in relevant_bids
        if len(software[software_name]["bids"]) < amount:
            print "bidding min amount as there are more packages than bids"
            bid_price = 5
        else: 
            relevant_min_bid_price = software[software_name]["bids"][0][1]
            # bid 5$ price < 100 else bid 10$
            if relevant_min_bid_price < 100:
                bid_price = relevant_min_bid_price + 5
            else:
                bid_price = relevant_min_bid_price + 10
        # dont exceed software's max_bid
        if bid_price >= max_bid:
            print "bid would exceed software's max_bid parameter"
            return
        if total_bid_sum + bid_price >= total_max_bid:
            print "total bid price exeeds total_max_bid parameter"
            print "out of funds"
            return
        if engaged:
            # do real bidding
            browser.open(topic_post_url)
            # View available forms
            #for f in browser.forms():
            #    print "FORM:"
            #    print f

            # Select the first (index zero) form
            browser.select_form(nr=0)

            message = "Bidding for " + software_name + " $" + str(bid_price)
            # post message
            browser.form['message'] = message

            browser.method = 'POST'
            # send !
            response = browser.submit(name='post')
            print "placed bid in forum:", message
            total_bid_sum += bid_price
            print "TOTAL bid sum so far:", total_bid_sum
        else:
            print "not engaged: would be BIDDING $", bid_price, "on", software_name

            
def main():
    browser = login(username,password)

    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print "This script bids in the KVR audio forum charity - bid for the charity!"
    print "make sure to adjust the parameters in the variable section well"
    print "the used forum search does not always return all necessary results as people spell the packages differently"
    print "also pay attention to the regexpressions not to be too greedy and match wrong numbers"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    raw_input("Press Enter to continue...")
    
    while True:
        for software_name in software:
            bid_software(browser, software_name)
        print "------------------------------------------------"
        print "TOTAL bid sum:", total_bid_sum, "after this cycle"
        print "------------------------------------------------"
        if not engaged:
            print "ran only once as we are not live (engaged = False)"
            quit()
            
if __name__ == "__main__":
    main()
    


    

# Garbage...
# # parse for pagination div
# pagination_div = soup.findAll("div",{"class": "pagination"})[0]
    
# thread_last_page_url = pagination_div.findAll("a")[-1]["href"]
    
# number = re.compile('\d+')
# thread_nr_of_posts = number.match(pagination_div.text).group()
    
# thread_posts_content = soup.findAll("div",{"class": "content"})

    

# Automate browser the easy way.
### Python library to automate webbrowser.

**Most functionality is tested on Chrome and Firefox, but may work on others as well.**  
This library made my working process of browser automation much easier,
hope it will help your team too.  
Here you can see short information about the module, but to see what is available,  
make sure to check documentation of available functions.
***

# Quick examples of usage


### 1. Initialize the browser


```python
# at first, initialize BrowserHelper object
from br_helper.br_helper import BrowserHelper

br =  BrowserHelper(browser="chrome", # you can also use firefox here
                    driver_path='/home/tornike/Desktop/bin/chromedriver')

# useful notes:
# it you want to use same browser and driver_path most of the time,
# after the installation you can run second line without
# driver_path argument and follow the instructions in terminal/interpreter.

# In this case, module will try to scan your system and find
# any file with "chromedriver" or "geckodriver"(in case of firefox) 
# in name, then it lists all matches, and you can choose which one to use
# by default if no driver_path argument is passed.

# in previous step you can also pass full file path of driver
# to use, if it is not listed,

# ! make sure you are using appropriate version of 
# chromedriver/geckodriver for your chrome/firefox browser !
```


```python
# if you want to use proxy, with hidden browser(maybe to run on server without GUI),  
# and also hide images on pages, and use custom download location, you can supply options  
# argument when creating an object, with similar form: 
br = BrowserHelper("chrome",
                   driver_path='your_driver_file_path',
                   options={
                            'proxy': 'ip_address:port_number',
                            'visibility': False,
                            'hide_images': True,
                            'download_location': 'your_folder_path'})
```

**All keys that you can use in previous step**
<pre>
   Key name                 Value                   Value Type       
--------------------------------------------------------------
* visibility            - True/False                - boolean
* download_location     - /path/to/folder           - string
* window_size           - (width, height)           - tuple
* hide_images           - True/False                - boolean
* disable_javascript    - True/False                - boolean
* proxy                 - ip:port                   - string
* user_data_dir         - path/to/chrome/profile    - string
* disable_infobars      - True/False                - boolean
</pre>
  
***

### 2. Basic examples


```python
# get a webpage
br.get("example.com")

# click on an element with partial text match
br.find("More").click()
# find is a powerfull method, check its documentation ( type: >>>help(br.find) )
# to see how you can make case insensitive, exact or specific
# tag-based element searches with just text

# in some cases, it is  better to use the method click,
# and pass matched element, which will try to click element using
# javascript, and by default try to click its parent in case of error.
# see click method for more information (type >>>help(br.click) )

# go back in history
br._b()
# and forward
br._f()
```


```python
# scroll to the bottom
br.bottom()
# go back
br.top()
# refresh
br.r()

# log some information
br.log_info("successfully refreshed the page")
# after this step, check new log.txt file in your current working directory.
# To use different log file, just pass log_file argument when initializing br object,
# with preferred full path of log file to use later.

# get new page
br.get("uct.ge")
```

```python
# locating elements to interact with them

# click on first matching element
# by css selector
br.css1("a#programming").click()
# or use xpath
br.xpath1("//a[@id='programming']").click()
# you will get an IndexError if element was not found,
# so you can consider using css, or xpath, instead of css1 and xpath1 methods
# and check if returned list is not empty to continue working.
```


```python
# locating elements to parse a webpage data
elements = br.bcss(".class_of_your_element")
# here first 'b' stands for bs4 library, which is used with this method
# we also have bcss1 to find first match.
```


```python
# wait until specific loader, or other element disappears
br.wait_until_disappears("type_your_css_or_xpath_selector_of_loader_here")
```


```python
# take a screenshot
br.google("why to visit Georgia")
br.screenshot(image_name='screenshot.png')
```


```python
# run javascript code
really = br.js('console.log("Python is cool"); return true')
```


```python
# login to a website
br.login("facebook.com", ("username", "password"))
br.login("twitter.com/login", ("username", "password"))
br.login("linkedin.com", ("username", "password"))

# if you want to check if login was successfull
# in most basic cases you can rely on returned value of login method
# otherwise, define your own logic, for example
if br.login("twitter.com/login", ("your_username", "your_password")):
    print("Hello, twitter")
else:
    print("Unsuccessfull login")
```


```python
# if you are tired, try
br.mario()  # we do not have reliable methods to play it yet...
```


```python
# or have some fun with this few lines of code
br.dino() # works for Google Chrome

import time, random

while True:
    time.sleep(random.randint(1, 5)/10)
    br.press("up")  # ! this method is still in development !
```


```python
# Please do not try this!
br.get("finder.ge")
br._dance()
```


### 3. Run multiple browser instances in parallel(almost)
Module has helper class, for cases when we want to run more than one instance of browser at the same time. It allows you to automatically split given urls into number of instances that you want to get using browser, get them and call callback function after each request.
That specific class uses information about DRIVER_PATH, that was defined earlier, so make sure before using it to define path in modules file itself, or just initialize BrowserHelper class instance without giving driver_path and when it finds correct driver path, type the number of it in terminal to save it in file automatically(this method of getting information will probably change in next releases).

Here is an examples of using it, with explanations:

#### Example 1


```python
'''
    Code to download multiple files using given urls.
    Each given url should return file directly, when opened.

    Please take into account the fact that in this example 
    we use very simple lambda expression as our callback argument
    to just print urls, not waiting until downloads finish,
    so in real cases, you may want to use a bit more complex function,
    which also waits before downloads are completed.
'''

from br_helper.br_helper import MultiBr
import os

# url pattern to use (I found that site recently to test the functionality)
urls = ['http://ipv4.download.thinkbroadband.com/1MB.zip' for i in range(100)]

# initialize
mbr = MultiBr()

# start processes
mbr.get_with_multi(
        # use thread
        multi_type="thread",
        # number of threads
        multi_num=5,
        # options for BrowserHelper instance
        options={"download_location": os.path.abspath("downloaded_files")},
        # direct download urls
        urls=urls,
        # just print url
        callback=lambda br: print(br.meta['url'])
    )
###########
# Enjoy ! #
###########

```

#### Example 2


```python

'''
    what test does:
        Opens few browser instances
        using separate threads/processes,

        loads finder.ge-website, searches for specific
        word, parses returned page data and saves
        results in json lines or csv file.

    # make sure that in br_helper you have already saved driver location #
'''

from br_helper.br_helper import MultiBr
import time

# for now, module is mainly designed for get requests
# but we can do also posts this way
# not most efficient, but should work


##########################################
# define file format to save results in
##########################################

CASE = "csv"  # comma separated values

# CASE = "jl"   # json lines

##########################################


# define what words we want search for
search_words = ["Javascript", "C#", "PHP", "Python", "Golang", ""] * 3

# say that we want to get same urls multiple times
main_url = "finder.ge"
urls = [main_url for i in search_words]


# define callback function
# it will be called every time browser loads our url
def callback(br):
    '''
    when called, br_helper object (browser) will be passed here.
    Also in each case we will have access to requested page-s url
    with br-s meta dictionary(using url key).

    If we supplied other meta data, in get_with_multi method
    we will have access to this data here.
    '''

    # at first, make sure that there are no clicks needed
    # (site specific - go to finder.ge first time to see it)

    if br.find("თანხმობა", all_=True):
        br.find("თანხმობა").click()
        br.find("გაგრძელება").click()
        br.find("აღწერა").click()

    # search
    # with urls we also will pass word as meta data, so get it here

    time.sleep(2)  # to avoid dos restriction(503)
    search_word = br.meta["search_word"]

    # Just in case print check
    print(br.meta["url"])

    # find input(for different selectors see br_helper's methods)
    br.css1("input[placeholder]").send_keys(search_word)
    br.css1("input[value='ძიება']").click()
    # breakpoint()

    # get data (not the most reliable way)
    #######################################
    if CASE == "jl":
        ######################################
        # jl case (generate dictionary)
        ######################################
        data = [{k: j.strip() for j, k in
                zip(i.text.split("\n"), 
                    ["დასახელება", "კომპანია", "ბოლო ვადა"])}
                for i in br.css("div.content")]

        # we can save data here, by hand,
        # but this time we are going
        # to set save_results argument to True, so
        # data returned from this function
        # will be saved in
        # jl file named data_CURRENT_TIME.jl

        return {
            "search_word": search_word,
            "vacancies_data": data}
        ######################################
    elif CASE == "csv":
        #######################################
        # csv case (generate list)
        ######################################
        data = [[search_word] +
                i.text.split("\n") for i in br.css("div.content")]
        headers = ["სიტყვა", "დასახელება", "კომპანია", "ბოლო ვადა"]

        return (headers, data)
        #######################################


# supported save methods for now
assert CASE in ['jl', 'csv']

# initialize
mbr = MultiBr(save_format=CASE)  # save jl or csv

# start processes
mbr.get_with_multi(
        multi_type="thread",  # we can use process or thread here
        multi_num=5,           # how many of them
        options={},            # options to use in browser in br_helper class
                               # useful if we want to pass different proxies,
                               # in which case options will be list of
                               # options dicts

        urls=urls,             # all urls we want to load
        callback=callback,     # our function above
        save_results=True,     # do we want to save callback answers in jl
                               # or csv file?

                               # if we are adding meta data, it should be
                               # list of dictionaries with same length
                               # and sequence as urls and all data in
                               # these dictionaries will be available
                               # in callback in br.meta dictionary.
                               # do not use url as keys, it will be added
                               # with information about requested/
                               # not redirected(if that is the case)
                               # url, every time automatically
        meta=[{"search_word": i} for i in search_words]
    )
```

# Installation methods
1. pip install br-helper
2. git clone https://github.com/Tornike-Skhulukhia/browser_automation_helper

# Dependencies
1. selenium
2. beautifulsoup4

### And downloaded
* chromedriver - if you want to use Chrome
* geckodriver - if you want to use Firefox

# Python version
Code is tested on **Python3.6** and above


'''
    Test new + old module's functionality.

    what test does:
        Opens few browser instances
        using separate threads/processes,

        loads finder.ge-website, searches for specific
        word, parses returned page data and saves
        results in json lines or csv file.

    # make sure that in br_helper you have already saved driver location #
'''

from multi_br import MultiBr
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
# it will be celled every time browser loads our url
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

        # print("headers:", headers)
        # print("data:", data)
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

###########
# Enjoy ! #
###########

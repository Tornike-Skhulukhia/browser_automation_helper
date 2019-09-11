'''
    Code to download multiple files from website using MultiBr class
'''

from multi_br import MultiBr
import os

# url pattern to use
url_base = 'https://this_page_does_not_exists_.html/page-{}'

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
        urls=[url_base.format(i) for i in range(1000)],
        # just print url
        callback=lambda br: print(br.meta['url'])
    )
###########
# Enjoy ! #
###########

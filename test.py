'''
    Example of opening javascript disabled
    chrome browser with random proxy and
    checking current ip address.
'''

from br_helper import BrowserHelper
# using module - https://github.com/Tornike-Skhulukhia/proxy
from proxy.proxy import Proxy

p = Proxy()
# get 1 proxy address
# hopefully we will find proxy with this timeout
ip_port = p.get_proxy(1, timeout=0.5, v=True)

# initialize browser object
br = BrowserHelper(options={
                            "proxy":ip_port,
                            "disable_javascript": True,
                           })
# check ip
br.ip()
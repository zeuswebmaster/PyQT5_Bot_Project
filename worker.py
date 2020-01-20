import threading
from corporationwiki import CorporSearch


def do_crawl_corpor(keyword, log_callback):
    print ("param name: {}".format(keyword))
    print ("param log callback: {}".format(log_callback))

    corporSearch = CorporSearch(keyword, log_callback)
    corporSearch.parse_page()
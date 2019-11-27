
import csv
import json
import os
import time

from bs4 import BeautifulSoup as bs
from selenium import webdriver


#################################################
########   Define your driver path here   #######
#################################################

DRIVER_PATH = ""


class BrowserHelper:
    '''
    class to help automate browser
    '''
    def __init__(self,                 browser="chrome",
                 driver_path=None,     options=False,       add_arguments=[],
                 log_file="log.txt"):
        '''
        initialize object with given arguments:
            1. browser - browser to work with("chrome" or "firefox").
                        currently development uses chrome,
                        but firefox has support for basic functionality.

            2. driver_path - driver file location(appropriate for browser).
                            Takes precedence over global DRIVER_PATH variable.

                            If when creating object this argument was not
                            supplied, we will try to use already globally
                            defined DRIVER_PATH variable's value,
                            which at first is "", but if we wait few seconds
                            to find possible candidates for driver path and
                            after that type appropriate index to save as
                            DRIVER_PATH value, this change will automatically
                            happen in this file, so next time we can
                            create objects without using driver_path argument.

                            Of course, it is also possible to make this change
                            by hand first time in this file.

            3. options - dictionary of options to use for specific browser
                        instance. currently supported:
                            . visibility             (boolean)
                            . download_location      (string)
                            . window_size            (tuple)
                            . hide_images            (boolean)
                            . disable_javascript     (boolean)
                            . proxy                  (string)
                            . user_data_dir          (string)
                            . disable_infobars       (boolean)

                        see _add_necessary_options for more details.

            4. add_arguments - list of arguments to add with selenium browser 
                            instance's add_argument method, before launching browser.
                            (default=[])

            5. log_file - log file to use in self.log method.
                         default=("log.txt")
        '''
        if driver_path is None:
            # maybe variable is defined
            global DRIVER_PATH

            if DRIVER_PATH:
                self.driver_path = DRIVER_PATH  # no checks here
            else:
                self.driver_path = self._get_driver(browser)
                if not self.driver_path:
                    exit()
                else:
                    # dynamically edit lines in this file
                    self._replace_driver_path_line_if_necessary(
                                                        self.driver_path)
        else:
            self.driver_path = driver_path

        self.br = False
        self.log_file = log_file
        # for later use
        self.keys = ""

        self.options = options  # supply dictionary
        self.add_arguments = add_arguments
        self.which_browser = browser

    def __repr__(self):
        ''' Representation '''
        text = (f"< BrowserHelper (browser={repr(self.which_browser)}, "
                f"driver_path={repr(self.driver_path)}, "
                f"options={repr(self.options)}) > ")
        return text

    def __str__(self):
        ''' What to print '''
        text = f'<BrowserHelper object for {self.which_browser}>'
        return text

    def _replace_driver_path_line_if_necessary(self, driver_path):
        '''
        replace current files DRIVER_PATH line,
        if user gives this information when needed,
        to not repeat same process more than once.

        adds appropriate string in line
        DRIVER_PATH = ""
        plus comment before that line that it changed dynamically
        '''
        import os
        import sys
        import re

        try:
            # works for scripts usage
            curr_file = os.path.abspath(os.path.realpath(__file__))
        except:
            # added for shell support, as __file__ is not defined here
            # may need modification/refinement
            curr_file = os.path.join(os.getcwd(), sys.argv[0])

        # read
        with open(curr_file, "r") as f: content = f.read()
        # edit
        notif_line = ('""" Line Changed Automatically At'
                      f'| {time.ctime()} """')

        content = re.sub(
            '\nDRIVER_PATH = ""\n',
            f'\n{notif_line}\n'
            f'DRIVER_PATH = "{driver_path}"\n', content)

        # write
        with open(curr_file, "w") as f: f.write(content)
        print(f"Driver location {self.driver_path} saved".center(70))
        # be careful here

    def _get_driver(self, browser):
        '''
        Search file system and get driver files locations.

        Then ask, which one to use, if none found, tell about it,
        and try to get this info from user, otherwise exit.

        P.s. here we have an infinite loop.
        '''
        from pathlib import Path
        import os

        drivers = {"chrome": "chromedriver",
                   "firefox": "geckodriver",
                   # "test": "this_file_should_not_be_found",

                   }

        if browser not in drivers:
            print(f"Sorry, {browser} is not supported yet")
            return

        driver_name = drivers[browser]
        possible_drivers = []

        print(f'Searching for driver files for {browser}'.center(70))

        try:
            for i in Path("/").glob(f"**/*{driver_name}*"):
                link = str(i).lower()

                if driver_name in link:
                    # check that file is .exe(windows) or has no extension
                    # for now, avoid complications with system types
                    if link.split(".")[-1] == "exe" or \
                            any([link.endswith(j) for j in drivers.values()]):
                        # path seems to be not working correctly
                        # so make check
                        possible_drivers.append(i)
        except OSError:
            pass  # sometimes error appears at the end, bug (?)

        # check answer
        if not possible_drivers:
            print(
                f"Sorry, drivers for {browser} not found, please download one."
                "\nChrome  - http://chromedriver.chromium.org/downloads"
                "\nFirefox - https://github.com/mozilla/geckodriver/releases"
                "\n\nexiting")
            return
        else:
            print("="*70, "\n")
            print(f"{len(possible_drivers)} possible driver files found,"
                  " which one should I use?".center(70))
            print("* P.s. you can also supply full path to driver here\n")
            print("="*70, "\n")

            for index, i in enumerate(possible_drivers):
                print(f' {index}. {i}')

            answer = input().strip()

            # else:
            while not os.path.isfile(answer) or not answer.isdigit():
                if answer.isdigit():
                    index = int(answer)
                    max_good_index = len(possible_drivers) - 1

                    if not (0 <= index <= max_good_index):
                        print(f"Please use index between 0 and {max_good_index}")
                    else:
                        print(f"Thanks,")
                        return possible_drivers[index]
                else:
                    print("File not found, try again")
                answer = input().strip()

            print(f"Thanks,")
            return answer

    def _add_necessary_options(self, args):
        '''
        change/add options to browser instance,
        such as custom download location,
        proxy address, visibility(hide/show browser)

        args --> dictionary, ex: {'proxy' : '1.2.3.4:5', 'visibility': False }
        full list:
            . visibility            - True/False                - boolean
            . download_location     - /path/to/folder           - string
            . window_size           - (width, height)           - tuple
            . hide_images           - True/False                - boolean
            . disable_javascript    - True/False                - boolean
            . proxy                 - ip:port                   - string
            . user_data_dir         - path/to/chrome/profile    - string
            . disable_infobars      - True/False                - boolean
                                                                    (default=True)
        '''
        if self.which_browser == "chrome":
            from selenium.webdriver.chrome.options import Options
        elif self.which_browser == "firefox":
            from selenium.webdriver.firefox.options import Options

        self.browser_options = Options()

        # things to change by default
        self.browser_options.add_argument("--disable-infobars")

        # add add options
        for argument in self.add_arguments:
            self.browser_options.add_argument(argument)

        if self.options:
            for key, value in self.options.items():
                # proxy
                if key == "proxy":
                    self.browser_options.add_argument(
                        f"--proxy-server={value}")

                # window size
                elif key == "window_size":
                    self.browser_options.add_argument(
                        f'--window-size={value[0]},{value[1]}')

                # download folder
                elif key == "download_location":
                    add_me = {'download.default_directory': value}
                    self.browser_options.add_experimental_option(
                                                     'prefs', add_me)
                # display or not images
                elif key == "hide_images":
                    if value:
                        self.browser_options.add_argument(
                            '--blink-settings=imagesEnabled=false')

                # disable or not javascript
                elif key == "disable_javascript":
                    if value:
                        self.browser_options.add_experimental_option(
                                        "prefs",
                                        {'profile.managed_default'
                                         '_content_settings.javascript': 2})

                elif key == "disable_infobars":
                    if not value:
                        # self.browser_options.add_argument(
                        #                         "--enable-infobars")
                        self.browser_options.arguments.remove(
                                                        "--disable-infobars")

                # hide or not browser window
                elif key == "visibility":
                    if not value:
                        self.browser_options.add_argument('--headless')

                # chrome profile to use
                elif key == "user_data_dir":
                    self.browser_options.add_argument(
                                f'user_data_dir={value}')

                # to avoid possible quiet bugs
                else:
                    exc_text = repr(key) + " is not a valid option yet\n"
                    exc_text += ("""Avaliable options are:
                        . visibility
                        . download_location
                        . window_size
                        . hide_images
                        . disable_javascript
                        . proxy
                        . user_data_dir
                        . disable_infobars""")

                    raise Exception(exc_text)

    def _initialize_browser_if_necessary(self):
        '''
        initialize(open and assign to object) browser if necessary
        '''
        if not self.br:
            # for later use
            from selenium.webdriver.common.keys import Keys

            self._add_necessary_options(self.options)
            # breakpoint()

            if self.which_browser == "chrome":

                self.br = webdriver.Chrome(executable_path=self.driver_path,
                                           options=self.browser_options)
            elif self.which_browser == "firefox":
                self.br = webdriver.Firefox(executable_path=self.driver_path,
                                            options=self.browser_options)
            self.keys = Keys

    def close(self):
        '''just close browser'''
        self.br.quit()

    def _get_interactables(self, webelements):
        '''
        get list of webelements(selected with xpath/css)
        and return only those, which seems interactable.

        # method needs refinement #
        '''
        return [i for i in webelements if i.is_displayed() and i.is_enabled()]

    def css(self,            selector,                 interactable=False,
            highlight=False, print_command=False):
        '''
        Find all matching webelements by css selector.

        arguments:
            1. selector - selector to use

            2. interactable - if set to True(default=False), only possibly
                            interactable elements will be returned

            3. highlight - set to True to highlight matched element
                        using _change_selection_look method
                        (default=False).

            4. print_command - if set to True, javascript code
                            that was used in _change_selection_look
                            method will be printed(default=False).
        '''
        matches = self.br.find_elements_by_css_selector(selector)

        if interactable:
            matches = self._get_interactables(matches)

        # highlight matches
        if highlight:
            self._change_selection_look(selector, print_command)

        return matches

    def css1(self,            selector,                 interactable=False,
             highlight=False, print_command=False):
        '''
        Find first matching webelements by css selector.

        If element is not present, exception will be raised.

        arguments(same as for css method):
            1. selector - selector to use

            2. interactable - if set to True(default=False), only possibly
                            interactable elements will be returned

            3. highlight - set to True to highlight matched element
                        using _change_selection_look method
                        (default=False).

            4. print_command - if set to True, javascript code
                            that was used in _change_selection_look
                            method will be printed(default=False).
        '''
        elem = self.css(
                selector, interactable, highlight, print_command)[0]
        return elem

    def xpath(self,              selector,               interactable=False,
              highlight=False,   print_command=False):
        '''
        Find all matching webelements by xpath selector.

        arguments:
            1. selector - selector to use

            2. interactable - if set to True(default=False), only possibly
                            interactable elements will be returned

            3. highlight - set to True to highlight matched element
                        using _change_selection_look method
                        (default=False).

            4. print_command - if set to True, javascript code
                            that was used in _change_selection_look
                            method will be printed.
        '''
        matches = self.br.find_elements_by_xpath(selector)

        if interactable:
            matches = self._get_interactables(matches)

        # highlight selected
        if highlight:
            self._change_selection_look(selector, print_command)

        return matches

    def xpath1(self,              selector,               interactable=False,
               highlight=False,   print_command=False):
        '''
        Find first matching webelement by xpath selector.

        arguments:
            1. selector - selector to use

            2. interactable - if set to True(default=False), only possibly
                            interactable elements will be returned

            3. highlight - set to True to highlight matched element
                        using _change_selection_look method
                        (default=False).

            4. print_command - if set to True, javascript code
                            that was used in _change_selection_look
                            method will be printed.
        '''
        elem = self.xpath(selector, interactable)[0]
        return elem

    def find(self,                      text,
             ignore_case=False,         tag="*",
             all_=False,                exact=False,
             interactable=True,         print_selector=False,
             highlight=False,           print_command=False):
        '''
        Convenient way to find elements on page,
        using exact, or partial text match.

        arguments:
            1. text - text to find(text that is in element we are searching)

            2. ignore_case - set to True to ignore upper
                            and lower cases(default=False)

            3. tag - set to valid html tag to narrow down results
                    (ex: p, div, span) (default="*" - (everything))

            4. all_ - set to True to get list of all matches
                    (default=False - returns first match,
                    or raises exception if not found)

            5. exact - set to True to find elements containing
                     given text only(default=False)

            6. interactable - set to False to get really all matches
                            (default=True, so only elements that seem
                            interactable will be returned, see
                            _get_interactables method for more details)

            7. print_selector - set to True to print generated selector
                              (default=False)

            8. highlight - set to True to highlight matches with
                        _change_selection_look method (default=False)

            9. print_command - set to True to print javascript
                            code that is executed when using
                            _change_selection_look method (default=False)
        '''

        if not ignore_case:
            if exact:
                sel = f'//{tag}[text() = "{text}"]'
            else:
                sel = f'//{tag}[text()[contains(.,"{text}")]]'
        else:
            uppers = "".join(sorted(set(text.upper())))
            lowers = "".join(sorted(set(text.lower())))

            if exact:
                sel = (f"""//{tag}[translate(text(), '{uppers}', """
                       f"""'{lowers}') = '{text.lower()}']""")
            else:
                sel = (f"""//{tag}[text()[contains(translate(., '{uppers}', """
                       f"""'{lowers}'), '{text.lower()}')]]""")

        # print selector if we want
        if print_selector:
            print(sel)

        # breakpoint()
        # highlight selection
        if highlight:
            self._change_selection_look(sel, print_command)

        # do not check for interactability
        if not interactable:
            answer = self.xpath(sel, print_command)

            if not all_:
                answer = self.xpath1(sel)

        else:
            answer = self.xpath(sel)

            answer = [i for i in answer if
                      i.is_displayed() and i.is_enabled()]
            if not all_:
                # raise error if no interactable element found
                answer = answer[0]

        return answer

    def select(self, select_it, by="text", select_tag="select"):
        '''
            select specific option from select tag.
            
            arguments:
                1. select_it - actual index, value or text we are looking for.
                                +support of negative indexing(It is Python :-) )

                2. by - "index", "value" or "text" 
                        use whichever you want(default="text"),
                        with appropriate data type for each one,
                        (index - INTEGER, value - STRING, text - STRING)

                3. select_tag - selector for select tag(
                        default="select", so it uses first select tag on page)
        '''
        from selenium.webdriver.support.ui import Select

        select = Select(self._css1_xpath1(select_tag))

        # to allow negative indexing
        if by == "index" and select_it < 0:
            select_it = len(select.options) - abs(select_it)

        call_me = f'select_by_{by if by != "text" else "visible_text"}'
        
        getattr(select, call_me)(select_it)

    def get(self, url_or_urls, add_protocol=True, callback=False):
        '''
        load url page.

        if browser is not initialized yet, it will
        start with given options

        arguments:
            1. url_or_urls - where to go, if it is a list,
                            all urls will be loaded in sequence.

            2. add_protocol - if set to False(default=True),
                            exact url load will be tried,
                            otherwise, if url is not starting
                            with http:// or https:// , we will add http://.
                            This makes process of page retrieval easier,
                            as we do not need to type http:// every time,
                            just br.get("example.com") will work.

            3. callback - if supplied(Default=False) this function
                          will be called after page loads
                          with this class object as an argument.

                          we may use it to parse and save data somewhere.
        '''
        # initialize browser
        self._initialize_browser_if_necessary()

        # convert to list if it is string
        if isinstance(url_or_urls, str):
            url_or_urls = [url_or_urls]

        # add http:// if needed
        if add_protocol:
            for index, url in enumerate(url_or_urls):
                if url.split("//")[0].lower() not in ["http:", "https:"]:
                    url_or_urls[index] = "http://" + url

        if callback:
            for index, url in enumerate(url_or_urls):
                self.br.get(url)
                callback(self)
                if len(url_or_urls) > 1:
                    print(f'{index + 1:^4}/{len(url_or_urls):^4}| {url} | + ')
        else:
            for index, url in enumerate(url_or_urls):
                self.br.get(url)
                if len(url_or_urls) > 1:
                    print(f'{index + 1:^4}/{len(url_or_urls):^4}| {url} | + ')

    def _b(self):
        '''
        go back in history
        '''
        self.br.back()

    def _f(self):
        '''
        go forward in history
        '''
        self.br.forward()

    def down(self):
        '''
        press down key
        '''
        self.press("down")

    def up(self):
        '''
        press up key
        '''
        self.press("up")

    def right(self):
        '''
        press right key
        '''
        self.press("right")

    def left(self):
        '''
        press left key
        '''
        self.press("left")

    def bottom(self):
        '''
        press end key to go to bottom of page
        '''
        self.press("end")

    def top(self):
        '''
        press home key to go top of page
        '''
        self.press("home")

    def pu(self):
        '''
        press page up key to go up one screen
        '''
        self.press("page_up")

    def pd(self):
        '''
        press page down key to go down one screen
        '''
        self.press("page_down")

    def _get_current_domain(self):
        '''
        returns current page's domain part
        '''
        import re
        domain = re.search(
                    r"(.*\://.*?)/", self.br.current_url).group(1)

        return domain

    def home(self):
        '''
        go to home page of opened browser page
        '''
        import re

        if self.br:
            domain = self._get_current_domain()
            self.get(domain, add_protocol=False)
        else:
            raise Exception("Please load browser first!")

    def log_info(self, text, also_print=True):
        '''
            Log given text in file that is assigned as log_file property.

            Current time and newline character will be added automatically
            after and before the text.

            arguments:
                1. text - text to log/save in file
                2. also_print - set to False if you do not want also
                                to print this text to screen(default=True)
        '''
        with open(self.log_file, "a") as f:
            line = f'{time.ctime()} | {text}\n'
            f.write(line)

        if also_print:
            print(line)

    def press(self, key, elem=False):
        '''
            Send keys to current window elements.
            # unfortunately not all of them work for now.

            arguments:
                1. key - key to press, upper or lowercase
                        (space, enter, up, down...).
                        here we use selenium.webdriver.common.keys keys.

                2. elem - element to send press(default=False).
                        if element is not supplied, body tag will be used.
        '''
        if not elem:
            elem = self.css1("body")

        key = getattr(self.keys, key.upper())
        elem.send_keys(key)

    def show_downloads(self):
        '''
        show downloads tab in browser,
        for now, works on chrome only.
        '''
        self.get("chrome://downloads/", add_protocol=False)

    def show_history(self, q=None):
        '''
        show history tab in browser,
        if q argument(string) is present, it will be searched in history.

        for now, works on chrome only.
        '''
        url = "chrome://history/"

        if q is not None:
            from urllib.parse import quote
            url += f"?q={quote(q)}"

        self.get(url, add_protocol=False)

    def show_settings(self, q=None):
        '''
        show settings tab in browser,
        for now, works on chrome only.

        If q argument is passed, it will be used to filter
        results on page.
        '''
        url = "chrome://settings/"

        if q is not None:
            from urllib.parse import quote
            url += f"?search={quote(q)}"

        self.get(url, add_protocol=False)

    def show_infos(self):
        '''
        show information about browser,
        such as versions, user agent & profile path.

        for now, works on chrome only
        '''
        self.get("chrome://version/", add_protocol=False)

    def ip(self):
        '''
        make duck duck go search to see
        current ip
        '''
        url = "https://duckduckgo.com/?q=my+ip&t=h_&ia=answer"
        self.get(url)

    def speed(self):
        '''
        go to website that checks internet speed
        for now it is https://fast.com
        '''
        url = "https://fast.com"
        self.get(url)

    def bcss(self, selector):
        '''
        bs4 css selector method.

        gets elements using bs4 & whole page source
        *it seems faster in most cases than direct webelements.
        '''
        self._soup = bs(self.br.page_source, "lxml")
        return self._soup.select(selector)

    def bcss1(self, selector):
        '''
        bs4 css1 selector method.

        get first match using bs4 & whole page source
        *it seems faster in most cases than direct webelements.
        '''
        return self.bcss(selector)[0]

    def js(self, comm):
        '''
        execute given command with javascript and get returned value
        '''
        return self.br.execute_script(comm)

    def zoom(self, to_percent):
        '''
        zoom to page by given number(%).
        ex: zoom(100) is default --> normal mode.

        arguments:
            1. to_percent - number for zoom value(without % sign)
        '''
        self.js(f'document.body.style.zoom = "{to_percent}%" ')


    def rotate(self, deg=30, element_or_selector="body",  interactable=True):
        '''
        rotates given element in browser window.

        arguments:
            1. deg - degrees to rotate element by(including negative numbers)
                    (default=30)
            2. element_or_selector - css selector or selenium element to rotate
                                    (default="body", or full page)
            3. interactable - interactable argument for
                                css/xpath selectors(default=True)
        '''
        # webelement case
        if isinstance(element_or_selector,
                      webdriver.remote.webelement.WebElement):
            element = element_or_selector
        else:
            element = self._css1_xpath1(element_or_selector,
                                        interactable=interactable)

        old_style_value = element.get_attribute("style").strip()
        new_style_part = ('display: block; '
                          f'-webkit-transform: rotate({deg}deg)')
        full_style = new_style_part

        if old_style_value:  # may still cause errors sometimes, but...
            full_style = old_style_value + "; " + new_style_part

        self.br.execute_script(
            f"arguments[0].setAttribute('style','{full_style}')", element)

    def google(self, s=None, domain="com"):
        '''
            Google given text with
            given google country domain
            (default=com)

            if no search string supplied,
            just google page will be opened.

            arguments:
                1. s - search string(default="")
                2. domain - google domain use in search(default="com")
        '''
        from urllib.parse import quote

        if s is None:
            url = f'google.{domain}'
        else:
            q = quote(s)
            url = f'google.{domain}/search?q={q}'

        self.get(url)

    def duck(self, s=None):
        '''
            Search given text with duckduckgo
            search engine.

            if no search string supplied,
            just duckduckgo page will be opened.

            arguments:
                1. s - search string(default="")
        '''
        from urllib.parse import quote

        # url = "google.com"

        if s is None:
            url = f'duckduckgo.com'
        else:
            q = quote(s)
            url = f'duckduckgo.com/?q={q}'

        self.get(url)

    def _css_xpath(self, selector, interactable=False):
        '''
            gets css or xpath selector method based on selector
        (differentiates xpath with /), calls it and returns list of
        results it founds.

        arguments:
            1. selector - selector to use
            2. interactable - interactable argument for css/xpath method
        '''
        method = self.xpath if selector.startswith("/") else self.css
        return method(selector, interactable)

    def _css1_xpath1(self, selector, interactable=False):
        '''
            gets css or xpath selector method based on selector
        (differentiates xpath with /), calls it and returns first
        result if founds, if present, otherwise raises exception.

        arguments:
            1. selector - selector to use
            2. interactable - interactable argument for css/xpath method
        '''
        return self._css_xpath(selector, interactable)[0]

    def _print_error(self):
        '''
        prints error using traceback module's format_exc method
        '''
        import traceback
        print(traceback.format_exc())

    def login(self,             url,       login_info=("username", "password"),
              selectors=None,   seconds=1):
        '''
        # still in development #

        Function tries to log us on a website and returns True,
        if it thinks, we did it successfully.

        arguments:
            1. url - login url(where username,
                               password and submit is
                                present in one page,
                                so, sorry gmail for now)
            2. login_info -
                        list/set/tuple of username and password.
                        default - ("username", "password")

            3. selectors - list/set/tuple of css/xpath selectors,
                            (if selector starts with /, we use xpath methods)

                            . username - username/email selector
                            . password - password selector
                            . submit   - submit button selector

                            . success_sel - 2 element tuple -
                                    (args_for_method, check_method),
                                    . args_for_method - method arguments to
                                    use when checking element existence
                                    on logged in page - string -
                                        ex:
                                            'arg_1, arg_2="abc"'

                                    . check_method - specific method name
                                    (string) of this class to use for search
                                    after page loads.

                                    In short, if we run check_method with
                                    args_for_method arguments,
                                    on page where login is not successfull,
                                    we should not get any matches.

                        # We should supply all of these, or None of these
                        If not supplied, our simple predictionn logic
                        will be used to find possible elements and if
                        something goes wrong, function will return False

            4. seconds - number of seconds to wait page to load completely
                         (default = 1). We want to make this process dynamic
                         & more reliable in the future.
        '''
        # logged in status
        status = False
        username, password = login_info

        try:
            self.get(url)
            # later add more reliable method
            # to let browser fully render js & load
            time.sleep(seconds)

            # generate possible selectors if necessary
            _sel = ["username", "password", "submit"]

            # selectors here does not include success check selector
            if selectors is None:   # sequence may need refinements
                _selectors = {
                        _sel[0]: "input[type='email'], input[type='text']",
                        _sel[1]: "input[type='password']",
                        _sel[2]: "[type='submit']"}
            else:
                # small check
                assert len(selectors) == 4

                _selectors = {i: j for i, j in zip(_sel, selectors)}

            # and create dictionary of
            # selector - html element
            elems = {}

            for name_, sel_ in _selectors.items():
                # select between xpath or css
                elems[name_] = self._css1_xpath1(sel_, True)

            # type data and press login
            elems["username"].send_keys(username)
            elems["password"].send_keys(password)
            elems["submit"].click()
            # later add more reliable method
            time.sleep(seconds)

            # check if logged in successfully
            # if this selector is not present, check
            # if password field  is still present
            # on page - not very reliable, but for now
            # should work in most cases

            # user supplied case
            if selectors:
                args, check_method = selectors[-1]
                try:
                    if eval("""check_method(""" + args.strip() + """)"""):
                        status = True
                except:
                    self._print_error()
            # our prediction case
            else:
                if not self._css_xpath(_selectors["password"], True):
                    status = True
        except:
            self._print_error()
        return status

    def r(self):
        '''
        refresh page
        '''
        self.br.refresh()

    def _editable(self):
        '''
        make page editable/normal, using javascript
        '''
        self.js('if (document.designMode == "on")'
                '{document.designMode = "off"}'
                ' else {document.designMode = "on"}')

    def _ba(self):
        '''
        Make page black and white/normal by injecting css into body tag.
        '''
        script = '''
            var text = "filter: grayscale(1)";
            var css_text = document.body.style.cssText;

            if (css_text.includes(text)){
                document.body.style.cssText = css_text.replace(text, "")
            }else{
                document.body.style.cssText = text + css_text
            }
        '''
        self.js(script)

    def _invert(self):
        '''
        invert colors on a page by injecting css into body tag.

        # not very good for black background pages
        '''
        script = '''
            var text = "filter: invert(100%);";
            var css_text = document.body.style.cssText;

            if (css_text.includes(text)){
                document.body.style.cssText = css_text.replace(text, "")
            }else{
                document.body.style.cssText = text + css_text
            }
        '''
        self.js(script)

    def dino(self):
        '''
        start chrome dinosaur game
        '''
        self.get("chrome://dino", add_protocol=False)

    def mario(self):
        '''
        start super mario bross game
        from site:
            https://supermariobros.io/full-screen-mario/mario.html
        '''
        url = "https://supermariobros.io/full-screen-mario/mario.html"
        self.get(url)

    def screenshot(self, image_name="screenshot.png"):
        '''
        Take a screenshot of current page

        arguments:
            1. image_name - image name/path to save screenshot
                            (default='screenshot.png').
        '''
        self.br.save_screenshot(image_name)

    def _get_js_result_nodes_generation_code(
                                        self,
                                        css_or_xpath_sel,
                                        print_command=False):
        '''
        returns code that can be evaluated in js to get js array
        named nodes, containing elements using
        matching given css or xpath selector.

        So, after executing result of that function in javascript,
        we will have variable node, containing all matches we want.

        arguments:
            1. css_or_xpath_sel - selector(css or xpath) to use
            2. print_command - if set to True, command will also be printed
                            (default=False)
        '''
        # which selection method do we have here
        sel_type = "css"
        if css_or_xpath_sel.startswith("/"):
            sel_type = "xpath"

        if sel_type == "xpath":
            # ! test ... !
            # do not add var before variable, to use nodes later
            answer = ('nodes = []; '
                      f'results = document.evaluate(`{css_or_xpath_sel}`,'
                      '                                          document); '
                      'while (node = results.iterateNext())'
                      '                               {nodes.push(node)}; ')
        else:
            # do not add var before variable, to use nodes later
            answer = f'nodes = document.querySelectorAll(`{css_or_xpath_sel}`); '

        # useful for debugging
        if print_command:
            print(answer)

        return answer

    def _change_selection_look(self, css_or_xpath_sel,
                               style="normal", print_command=False):
        '''
        change how selection matches look on browser,
        selections are saved in javascript as array, called nodes.

        later may add more style numbers to make
        different changes, or even more control, if necessary.
        '''
        #############################################################
        import random as r

        _colors = ["red",     "green",       "blue",
                   "lime",    "orangered",   "yellow",
                   "brown",   "coral",       "hotpink", "magenta"]

        if style == "crazy":

            # to make selections more fun in each case
            # font color
            color = r.choice(_colors)

            # do not change background too often
            # b_color = r.choice(["black", "white"])  # not very good

            # font size
            font_size = f'{r.randint(20, 40)}px'

            # text decoration
            _lines = ["underline", "overline",
                      "line-through", "underline overline"]
            _styles = ["solid", "double", "dotted", "dashed", "wavy"]

            text_decoration = (f'{r.choice(_lines)} {r.choice(_colors)} '
                               f'{r.choice(_styles)}')

            # font weight
            font_weight = r.randint(1, 9) * 100

            # text shadow
            text_shadow = (f'{r.randint(-30, 30)}px '
                           f'{r.randint(-30, 30)}px '
                           f'{r.randint(3,   20)}px '
                           f'{r.choice(_colors)} ')

            # text transforms
            _timing = ["linear", "ease", "ease-in", "ease-out", "ease-in-out"]
            transition = f"all {r.choice(_timing)} {r.randint(1, 20) * 1000}ms"

            _transforms = ["translate", "rotate", "scale", "skew"]
            _transform_type = r.choice(_transforms)

            if _transform_type == "translate":
                _t1 = r.randint(-100, 100)  # from -100 to 100
                _t2 = r.randint(-100, 100)  # from -100 to 100

                transform = f"translate({_t1}px, {_t2}px);"

            elif _transform_type == "rotate":
                transform = f"rotate({r.randint(-45, 45)}deg);"

            elif _transform_type == "scale":
                _s1 = r.randint(5, 20) / 10  # 0.5 through 2
                _s2 = r.randint(5, 20) / 10  # 0.5 through 2

                transform = f"scale({_s1, _s2});"

            elif _transform_type == "skew":
                _s1_ = r.randint(-180, 180)
                _s2_ = r.randint(-180, 180)

                transform = f"skew({_s1_}deg, {_s2_})deg;"

            # borders
            # do not overcomplicate to use all sides separate borders...
            _b_styles = ["dotted",   "dashed",
                         "solid",    "double",
                         "groove",   "ridge",
                         "inset",    "outset",
                         "none",     "hidden"]

            border = (f"{r.randint(1, 10)}px {r.choice(_b_styles)}"
                      f" {r.choice(_colors)} ")

            # border radius
            border_radius = r.randint(1, 40)

            # letter spacing
            letter_spacing = f"{r.randint(-5, 5)}px"

            # zoom randomly
            if r.randint(1, 5) == 5:
                self.zoom(r.randint(30, 300))

            # invert colors randomly
            if r.randint(1, 10) == 1:
                self._invert()

        else:
            # normal cases
            color = r.choice(["#FFF", "#000", "#777", "#00F", "#0F0", "F00"])
            font_size = ""
            text_decoration = "underline"
            font_weight = ""
            text_shadow = "5px 5px 5px #FFF"
            transition = "all ease-in-out 400ms"
            transform = ""
            border = f"1px dotted {r.choice(_colors)}"
            border_radius = ""
            letter_spacing = "1px"
            # b_color = ""   # not very good
        #############################################################

        # create arrays code
        create_nodes_js = self._get_js_result_nodes_generation_code(
                                                        css_or_xpath_sel)

        # add transitions first
        transition_js = (' nodes.forEach(function(i){i.setAttribute( '
                         f' "transition", "{transition}  !important; "){"}"})')
        self.js(create_nodes_js + transition_js)
        if print_command:
            print(create_nodes_js + transition_js)

        # add code to change elements styling
        styles_js = (' nodes.forEach(function(i){i.setAttribute( '
                     ' "style", '
                     f'" color:              {color}                 !important; '
                     f'  font-size:          {font_size}             !important; '
                     f'  text-decoration:    {text_decoration}       !important; '
                     f'  font-weight:        {font_weight}           !important; '
                     f'  text-shadow:        {text_shadow}           !important; '
                     f'  transform:          {transform}             !important; '
                     f'  border:             {border}                !important; '
                     f'  border-radius:      {border_radius}         !important; '
                     f'  letter-spacing:     {letter_spacing}        !important; '
                     # f'  !important;'  # to add more styles
                     '")})')
        # useful for degugging
        if print_command:
            print(styles_js)

        self.js(styles_js)

    def _dance(self, selector="body", interval=0.3, print_command=False):
        '''
        fun method to change looks of each matched
        element in browser, default selector
        argument is body, but *, p, a or any other could
        be used.

        interval argument(default=0.3) controls intervals
        between changes on a page
        '''
        while True:
            time.sleep(interval)
            self._change_selection_look(selector,
                                        style="crazy",
                                        print_command=print_command)

    def click(self, elem, try_parent=True):
        '''
        click on element, iven if selenium says,
        element is not clickable at point.

        arguments:
            1. elem - webelement object to click
            2. try_parent - if set to True(Default), if click
                        raises exception, we will try to click on
                        its direct parent

            # simplify try-excepts later #
        '''
        # breakpoint()
        import selenium

        temp = selenium.common.exceptions
        exc = [
            temp.ElementClickInterceptedException,
            temp.ElementNotInteractableException]


        try:
            elem.click()
        except (exc[0], exc[1]):
            if try_parent:
                try:
                    elem.find_element_by_xpath("parent::*").click()
                except (exc[0], exc[1]):
                    self.br.execute_script("arguments[0].click()", elem)
            else:
                self.br.execute_script("arguments[0].click()", elem)

    def wait_until_disappears(self,
                              selector,
                              check_interval=0.5,
                              print_progress=True):
        '''
        wait until specific element disappears from page.
        check if element is still interactive/visible with
        _get_interactables method.

        arguments:
            1. selector - selector of element(css or xpath)

            2. check_interval - time interval before next
                            attempt of element search on page.
                            (default=0.5)

            3. print_progress - if set to False, function will not print
                            that it waits (default=True)
        '''
        while self._css_xpath(selector, interactable=True):
            if print_progress: print("waiting...")
            time.sleep(check_interval)
        return

    def _sitemap(self):
        '''
        get sitemap of current website
        '''
        url = f'{self._get_current_domain()}/sitemap.xml'
        self.get(url, False)

    def _robots(self):
        '''
        get robots.txt file of current website
        '''
        url = f'{self._get_current_domain()}/robots.txt'
        self.get(url, False)

    def _parse_sitemap_urls(self, allowed_extensions=['zip', 'gz']):
        '''
        Returns loc tag links on current page that end with allowed extension.
        Should be used with opened sitemap page.

        arguments:
            1. allowed_extensions - to get link from loc tag,
                                    It needs to be ended with one of
                                    allowed extension (default=['zip', 'gz']).
        '''
        urls = []

        # get file urls
        for loc in self.bcss("loc"):
            url = loc.text
            if url.lower().split(".")[-1] in allowed_extensions:
                urls.append(url)
        return urls

    def download_sitemap_files(self,
                               sitemap_url,
                               allowed_extensions=['zip', 'gz'],
                               ):
        '''
        Loads sitemap page, and opens
        each link individually to download that file.

        To wait for all downloads, it is better to write
        small script by yourself, that checks number of files
        in necessary folder and does what you want.

        arguments:
            1. sitemap_url - url of sitemap page
            2. allowed_extensions - to get link from loc tag,
                                    It needs to be ended with one of
                                    allowed extensions (default=['zip', 'gz']).
        '''
        # load page
        self.get(sitemap_url)

        urls = self._parse_sitemap_urls(allowed_extensions)

        print(f'| {len(urls)} urls found |'.center(50, "="))

        # get home page, to avoid multiple file downloads prompt
        self.home()

        # open pages - download files
        self.get(urls)

####################################################

class MultiBr:
    '''
    class to use multiple browser_helper instances at the same time.
    '''

    def __init__(self, save_format="jl", indent_jl=True):
        '''
        # !
        Make sure that driver path is written in br_helper module
        before start using this class.
        ! #

        Arguments:
            1. save_format - jl or csv, format in which will save
                            data automatically, if needed(default="jl")

                            . if we choose jl, callback should return
                            dictionary to save in jl file
                            . for csv, callback should return two lists,
                            first for data that we want to save and second
                            for headers data, that will be added if needed

            2. indent_jl - indent or not json lines data(default=True)
        '''
        if save_format.upper() not in ["CSV", "JL"]:
            raise Exception("PLease use CSV or JL "
                            "for save_format argument value!")
        self.save_format = save_format
        self.indent_jl = indent_jl

        extension = 'jl' if save_format.upper() == "JL" else "csv"
        self.filename = f"data_{time.ctime()}.{extension}"

    def _split_urls_list(self, urls, number):
        '''
        split given urls list(not set!) into sublists, each one
        containing approximately same number of urls.

        For more convenience, result is the dictionary
        with numbers from 0 to given (number - 1) as keys
        and appropriate sublists as values.

        useful when using multiple processes, to pass
        these sublists as separate arguments.
        '''
        # breakpoint()
        link_num_per_proc = len(urls) // number

        if len(urls) % number != 0:
            link_num_per_proc += 1

        lists = {i: [] for i in range(number)}

        for num in lists:
            add_me = urls[
                num * link_num_per_proc: (num + 1) * link_num_per_proc]
            lists[num].extend(add_me)

        return lists

    def _add_csv_line_in_csv_file(self, headers, text_items):
        '''
        add line with given text_items in csv file.
        We do this after loading each individual url
        to save data that was returned from callback function

        we also need headers, as we may need
        to add it if not already added using other
        process/thread.
        arguments:
            1. headers - headers row items(list) -
                        will be added if we write in
                        file first time.
            2. text_items - list of items to write in a row.
                            Also could be list of lists to write
                            more than one row per page.
        '''
        # breakpoint()
        write_headers = not os.path.exists(self.filename)
        # print("write_headers:", write_headers)

        with open(self.filename, "a") as f:
            writer = csv.writer(f, delimiter=",")
            # headers
            if write_headers:
                # print("written headers", headers)
                writer.writerow(headers)
            # new row
            if text_items:
                if not isinstance(text_items[0], (list, tuple, set)):
                    # print("changed to list")
                    text_items = [text_items]

                for row_items in text_items:
                    # print("written row", row_items)
                    writer.writerow(row_items)

    def _add_line_in_jl_file(self, text, indent=True):
        '''
        add line in json lines file,
        we do this after loading each individual url
        to save data that was returned from callback function

        arguments:
            1. text - text to write in file
            2. indent - indent text or not(default=True, with value 4)
        '''
        with open(self.filename, "a") as f:
            f.write(json.dumps(
                        text, ensure_ascii=False,
                        indent=4 if indent else None) + "\n")

    def _open_new_browser_and_get_pages(
                                    self,
                                    urls,
                                    callback=False,
                                    options={},
                                    save_results=True,
                                    meta=False):
        '''
            opens new browser instance, gets
            given urls and calls callback function with
            instance of this class as an argument.

            # we may add meta attribute to pass meta data easier
            # that can be used in callback function later

            Useful to use with get_with_multiprocessing function.

            arguments:
                1. urls - list of urls to load

                2. callback - function to call after
                              page loads with browser
                              (
                                . locate elements
                                . return data to save or save it directly)

                3. options - options to use when creating
                            objects from br_helper class(default={}).

                4. save_results - if set to True, data that callback
                                function returns will be saved in jl file.
                5. meta - meta data that we want to have in each callback
                         function. this argument should be list of dicts with
                         same length as urls and with same sequence as urls.
                         it will be available as browser instance's
                         meta property and will always have at least
                         url as key that shows requested url(not redirected)

        '''

        # breakpoint()N:
        if meta is not False:
            if len(meta) != len(urls):
                raise TypeError(
                    "urls and meta arguments should have same lengths, not "
                    f"{len(urls)} and {len(meta)}")
        else:
            meta = ({} for i in urls)

        br = BrowserHelper(options=options)
        for url, _meta in zip(urls, meta):

            br.get(url)
            # run callback and save answer
            if callback:
                # add meta info to use in callback
                assert "url" not in meta   # do not use url in meta yourself

                _meta.update({"url": url})

                br.meta = _meta
                callback_res = callback(br)

                if save_results:
                    if callback_res:
                        if self.save_format.upper() == "CSV":
                            # in case of csv, callback should return 2 lists,
                            # 1 for headers and one for actual data
                            self._add_csv_line_in_csv_file(
                                            callback_res[0], callback_res[1])
                        elif self.save_format.upper() == "JL":
                            self._add_line_in_jl_file(
                                                callback_res, self.indent_jl)
                    else:
                        print("Please return dictionary of data "
                              "you want to save from callback function")
                        exit()

        # close browser after all urls are loaded
        br.close()

    def get_with_multi(self,
                       multi_type,
                       multi_num=1,
                       options={},
                       urls=[],
                       callback=False,
                       save_results=False,
                       meta=False):
        '''
        starts multiple processes, each of which
        does the following:

            1. multi_type - do we want to use "thread"-s or "process"-es.

            2. opens new browser instance with given options,

            3. get urls and executes callback function each time

            4. gets callback function's returned dictionary and appends
                    it in json lines file, named like
                        "data_Mon Aug  5 13:52:19 2019.jl",
                        where time shows current class creation time.

        arguments:
            1. multi_type - process or thread - way we want to do
                            achieve seeming/real parellelism.

            2. multi_num - number of processes/threads we want to use

            3. options  - options to use when creating br_helper objects.
                        if we want same options, we should supply
                        one dictionary, otherwise list of dictionaries
                        with same length as number of browser
                        threads/processes.

            4. urls - all urls to get data from

            5. callback - callback function to call each time after page loads,
                          with instance of this class as an
                          argument(default=False, or no callback).

                          in callback, we should locate elements,
                          and returned data to save as dict.

                          on each page load, answer of callback function
                          will be appended in json line file
                          called f"data_{time.ctime()}.jl",
                          where time current class object creation time
            6. save_results - do we want to save callback's returned dictionary
                            in a file or not(default=False)

            7. meta - meta data that we want to have in each callback
                         function. this argument should be list of dicts with
                         same length as urls and with same sequence as urls.
                         it will be available as browser instance's
                         _meta property and will always have at least
                         url as key that shows requested url(not redirected)
        '''

        if multi_type == "thread":
            from threading import Thread as use_it
        elif multi_type == "process":
            from multiprocessing import Process as use_it
        else:
            raise TypeError(
                        f"Please use thread or process, not {multi_type}\n")

        # get sublists for each process
        splitted_urls = self._split_urls_list(urls, multi_num)

        if not meta: meta = [{} for i in urls]
        # it was not primarily for that, but lets also split metas the same way
        metas = self._split_urls_list(meta, multi_num)

        # start processes
        for num in range(multi_num):
            time.sleep(1)  # make 1 second intervals between process/thread
            # breakpoint()
            use_it(
                target=self._open_new_browser_and_get_pages,
                args=(
                        splitted_urls[num],
                        callback,
                        options if isinstance(options, dict) else options[num],
                        save_results,
                        metas[num])
                ).start()
            print(f"{multi_type.title()} N:{num} started")

####################################################
# More cool functions here 
####################################################

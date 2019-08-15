
#################################################
########   Define your driver path here   #######
#################################################

DRIVER_PATH = ""

#################################################

import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver


class BrowserHelper:
    '''
    class to help automate browser
    '''
    def __init__(self,                 browser="chrome",
                 driver_path=None,     options=False,
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

            4. log_file - log file to use in self.log method.
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
        self.which_browser = browser

    def __repr__(self):
        ''' Representation '''
        text = (f"<BrowserHelper (browser={repr(self.which_browser)}, "
                f"driver_path='{self.driver_path}')>")
        return text

    def __str__(self):
        ''' What to print '''
        text = f'<BrowserHelper object for {self.which_browser}>'
        return text

    def _replace_driver_path_line_if_necessary(self, driver_path):
        '''
        replace current files DRIVER_PATH line,
        if user gives this information when needed,
        to not repeat same process more than once

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

        then as, which one to use, if none found, tell about it,
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
                        # path seems to not working correctly
                        # (or we should read its docs),
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
            . disable_infobars      - disable or not infobars   - boolean
                                                                    (default=True)
        '''
        if self.which_browser == "chrome":
            from selenium.webdriver.chrome.options import Options
        elif self.which_browser == "firefox":
            from selenium.webdriver.firefox.options import Options

        self.browser_options = Options()

        # things to change by default
        self.browser_options.add_argument("--disable-infobars")

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

    def find(self, text, ignore_case=False,
             tag="*", all_=False, exact=False,
             interactable=True, print_selector=False,
             highlight=False, print_command=False):
        '''
        # why contains sometimes do not find elements
        with exact matches ?  - possible bug #

        get element on a page containing given text
        (not exact text match, just
        any element containing that text,
        if we want exact match, set exact argument to True,
        but be careful, as sometimes whitespace is not visible)

        it is possible to make case insensitive search,
        if ignore_case is set to True

        We can also supply parent tag string, to
        narrow down results, for example, find
        only <a> tags with text 'Hello',

        by default tag is *, so we search for all matches.

        * cool tip:
            We can inject xpath selector parts(after*) for more specific
        elements, for example, we can set tag to:
            *[@title='Xpath Seems Also Cool']
        and result will be the element with given title attribute.

        all_ argument controls, if all matches should be returned.

        in some cases, to avoid errors, for example if we are not sure
        if element will be present, we can set all_ to True
        (default is False) and we will get empty list if no elements found,
        when in opposite case(default) we will get errrroor

        Set interactable to False, to get not
        interactable elements also
        '''

        if not ignore_case:
            if exact:
                sel = f'//{tag}[text() = "{text}"]'
            else:
                sel = f'//{tag}[contains(text(), "{text}")]'
        else:
            uppers = "".join(sorted(set(text.upper())))
            lowers = "".join(sorted(set(text.lower())))

            if exact:
                sel = (f"""//{tag}[translate(text(), '{uppers}', """
                       f"""'{lowers}') = '{text.lower()}']""")
            else:
                sel = (f"""//{tag}[contains(translate(text(), '{uppers}', """
                       f"""'{lowers}'), '{text.lower()}')]""")

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
        #######################################
        # to use new soup in bcss method
        self._soup = False
        #######################################
        # initialize browser
        # breakpoint()
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
            for url in url_or_urls:
                self.br.get(url)
                callback(self)
        else:
            for url in url_or_urls:
                self.br.get(url)

    def log_info(self, text):
        '''
            Log given text in file that is assigned as log_file property.

            Current time and newline character will be added automatically
            after and before the text.

            arguments:
                1. text - text to log/save in file
        '''
        with open(self.log_file, "a") as f:
            line = f'{time.ctime()} | {text}\n'
            f.write(line)

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

        # if it is first time of search on page
        # assign soup property
        if not self._soup:
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

    def _zoom(self, to_percent):
        '''
        zoom to page by given number(%).
        ex: _zoom(100) is default --> normal mode.

        arguments:
            1. to_percent - number for zoom value(without % sign)
        '''
        self.js(f'document.body.style.zoom = "{to_percent}%" ')

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
            Searhc given text with duckduckgo
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
                    breakpoint()
            # our prediction case
            else:
                if not self._css_xpath(_selectors["password"], True):
                    status = True
        except:
            self._print_error()
            breakpoint()

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

    def _game(self):
        '''
        start chrome dinosaur game
        '''
        self.get("chrome://dino", add_protocol=False)

    def screenshot(self, element_or_selector="", image_name="screenshot.png"):
        '''
        Save screenshot of full page or part of it.
        # Needs some fixes to work in all cases(ex: some images) #

        arguments:
            1. element_or_selector - WebElement object or selector
                                    (xpath or css) to find element and
                                    then save its screenshot.

                                    If set to empty string
                                    (which is default argument),
                                    full body's screenshot will be saved.

            2. image_name - image name/path to save screenshot
                            (default='screenshot.png').
        '''
        from PIL import Image
        from io import BytesIO
        # import selenium

        # webelement case
        if isinstance(element_or_selector,
                      webdriver.remote.webelement.WebElement):
            element = element_or_selector

        # empty string case - save full page
        elif element_or_selector == "":
            self.br.save_screenshot(image_name)
            return

        # specific element case
        else:
            # selector case
            element = self._css1_xpath1(element_or_selector)

        location = element.location
        size = element.size

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        # save screenshot of entire page
        png = self.br.get_screenshot_as_png()
        # open image in memory
        img = Image.open(BytesIO(png))

        img = img.crop((left, top, right, bottom))
        img.save(image_name)

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
                self._zoom(r.randint(30, 300))

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

####################################################
# More cool functions here
####################################################
# # test
# br = BrowserHelper()
# br.get(["finder.ge"])

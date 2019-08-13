'''
    ! class is in testing stage !

    Define class to use multiple browser_helper instances
    to get data using multiple processes/threads and work with it easier
'''
import csv
import json
import os
import time

# if __name__ == '__main__':
#     from br_helper import BrowserHelper
# else:
#     from .br_helper import BrowserHelper
from br_helper import BrowserHelper


class MultiBr:
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
                         _meta property and will always have at least
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


# ##########################################
# More cool functions here
# ##########################################

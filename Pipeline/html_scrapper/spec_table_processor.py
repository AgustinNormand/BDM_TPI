import logging

import lxml.html

class Spec_Table_Processor():
    def __init__(self):
        pass

    def process_specs_table(self, request_text):
        parsed = lxml.html.fromstring(request_text)
        #specs = parsed.find_class("ui-pdp-specs__table")[0]
        keys = parsed.find_class("ui-pdp-specs__table__column-title")
        values = parsed.find_class("andes-table__column--value")
        if len(keys) != len(values):
            logging.warning("Keys and values in spec table should be equally length")
        key_values = {}
        for value in zip(keys, values):
            key_values[value[0].text] = value[1].text
        return key_values

    def contains_specs_table(self, request_text):
        try:
            parsed = lxml.html.fromstring(request_text)
            specs = parsed.find_class("ui-pdp-specs__table")[0]
            result = True
        except Exception as e:
            result = False
        return result

import logging

import lxml.html

class Spec_Table_Processor():
    def __init__(self):
        self.common_attributes = ['Superficie total',
                                  'Superficie cubierta',
                                  'Ambientes',
                                  'Dormitorios',
                                  'Baños',
                                  'Cocheras',
                                  'Cantidad de pisos',
                                  'Disposición',
                                  'Antigüedad',
                                  'Expensas',
                                  'Departamentos por piso',
                                  'Número de piso de la unidad',
                                  'Orientación',
                                  'Tipo de departamento',
                                  'Bodegas',
                                  'Tipo de casa',
                                  'Superficie de terreno']

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
        for key in self.common_attributes:
            if key not in key_values.keys():
                key_values[key] = None
        return key_values

    def contains_specs_table(self, request_text):
        try:
            parsed = lxml.html.fromstring(request_text)
            specs = parsed.find_class("ui-pdp-specs__table")[0]
            result = True
        except Exception as e:
            result = False
        return result

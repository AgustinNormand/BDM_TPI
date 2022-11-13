class Records_Processor():
    def __init__(self, logger):
        self.logger = logger
        self.common_attributes = ['Aire acondicionado',
                                  'Dormitorios',
                                  'Superficie cubierta',
                                  'Baños',
                                  'Ambientes',
                                  'Superficie total',
                                  'Operación',
                                  'Inmueble',
                                  'Condición del ítem',
                                  'Tour virtual',
                                  'Línea telefónica']

    def contains(self, result, key, value):
        for x in result:
            if x[key] == value:
                return True
        return False

    def fetch_nested_value(self, record, keys):
        try:
            for key in keys:
                record = record.get(key)
            return record
        except:
            return None

    def fetch_attribute_by_id(self, record, attr_id):
        try:
            for attr in record["attributes"]:
                if (attr["id"] == attr_id):
                    return attr["value_name"]
        except:
            return None

    def process_record(self, record, expected_attributes):
        result = {}
        result["title"] = record["title"]
        result["permalink"] = record["permalink"]

        #result["city"] = self.fetch_nested_value(record, ["location", "city", "name"])
        #result["state"] = self.fetch_nested_value(record, ["location", "state", "name"])
        result["latitude"] = self.fetch_nested_value(record, ["location", "latitude"])
        result["longitude"] = self.fetch_nested_value(record, ["location", "longitude"])
        result["neighborhood"] = self.fetch_nested_value(record, ["location", "neighborhood", "name"])

        result["seller_id"] = self.fetch_nested_value(record, ["seller", "id"])
        result["seller_city"] = self.fetch_nested_value(record, ["seller_address", "city", "name"])
        result["seller_state"] = self.fetch_nested_value(record, ["seller_address", "state", "name"])
        result["real_estate_agency"] = self.fetch_nested_value(record, ["seller", "real_estate_agency"])
        result["seller_cancelations"] = self.fetch_nested_value(record,
                                                                ["seller", "seller_reputation", "metrics", "cancellations",
                                                                 "value"])
        result["seller_claims"] = self.fetch_nested_value(record,
                                                          ["seller", "seller_reputation", "metrics", "claims", "value"])
        result["seller_handling_time"] = self.fetch_nested_value(record, ["seller", "seller_reputation", "metrics",
                                                                          "delayed_handling_time", "value"])
        result["seller_sales"] = self.fetch_nested_value(record,
                                                         ["seller", "seller_reputation", "metrics", "sales", "completed"])

        result["currency_id"] = record["currency_id"]
        result["price"] = record["price"]

        for attr in expected_attributes:
            result[attr.lower()] = self.fetch_attribute_by_id(record, attr)

        return result

    def process_results(self, results):
        self.logger.info("Processing {} records".format(len(results)))
        processed_records = []
        for result in results:
            if self.contains(result["attributes"], "id", "DEVELOPMENT_NAME"):
                self.logger.info("Development real state ignored")
                continue
            processed_result = self.process_record(result, self.common_attributes)
            processed_records.append(processed_result) # Podría ya publicarlos en vez de hacer el append
            #self.logger.info("{}".format(result))
            #self.logger.info("{}".format(processed_result))
            #break # TODO Guardar en algun lado
        self.logger.info("All records processed")
        return processed_records

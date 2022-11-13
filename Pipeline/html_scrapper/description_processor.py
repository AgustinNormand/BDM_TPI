import lxml.html

class Description_Processor():

    def process_description(self, request_text):
        parsed = lxml.html.fromstring(request_text)
        description = str(parsed.find_class("ui-pdp-description__content")[0].text_content())
        description = description.replace("\r", "").replace("\n", "").replace("\r\n", "")
        return description
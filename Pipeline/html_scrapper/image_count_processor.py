import lxml.html

class Image_Count_Processor():
    def __init__(self):
        pass

    def process_image_count(self, request_text):
        parsed = lxml.html.fromstring(request_text)
        imgs = len(parsed.find_class("ui-pdp-gallery__wrapper"))
        if imgs == 1:
            imgs = len(parsed.find_class("ui-pdp-gallery__label"))
        return imgs
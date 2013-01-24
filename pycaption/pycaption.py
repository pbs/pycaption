from collections import defaultdict

class CaptionConverter(object):
    def __init__(self, captions=[]):
        self.captions = captions

    def read(self, content, caption_reader):
        try:
            self.captions = caption_reader.read(content)
        except AttributeError, e:
            raise Exception(e)
        return self

    def write(self, caption_writer):
        try:
            return caption_writer.write(self.captions)
        except AttributeError, e:
            raise Exception(e)


class BaseReader(object):
    def detect(self, content):
        if content:
            return True
        else:
            return False

    def read(self, content):
        return Captions()


class BaseWriter(object):
    def write(self, content):
        return content

class Style(object):
    def __init__(self):
        pass

class Caption(object):
    def __init__(self):
        self.start = 0
        self.end = 0
        self.nodes = []
        self.style = {}

class Captions(object):
    def __init__(self):
        self.styles = {}

        # Captions by language.
        # TODO: default empty 'en' value?
        self.captions = defaultdict(list)


    


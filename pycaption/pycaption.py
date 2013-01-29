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

class CaptionData(object):
    TEXT = 1
    STYLE = 2
    BREAK = 3

    def __init__(self, type):
        self.type = type
        self.content = None
        self.start = None

    @staticmethod
    def create_text(text):
        data = CaptionData(CaptionData.TEXT)
        data.content = text
        return data

    @staticmethod
    def create_style(start, content):
        data = CaptionData(CaptionData.STYLE)
        data.content = content
        data.start = start
        return data

    @staticmethod
    def create_break():
        return CaptionData(CaptionData.BREAK)
      
class Caption(object):
    """
    A single caption, including the time and styling information
    for its display.
    """
    def __init__(self):
        self.start = 0
        self.end = 0
        self.nodes = []
        self.style = {}

    def is_empty(self):
        return len(self.nodes) == 0

class CaptionSet(object):
    """
    A set of captions in potentially multiple languages,
    all representing the same underlying content.
    """
    def __init__(self):
        self._styles = {}

        # Captions by language.
        # TODO: default empty 'en' value?
        self._captions = defaultdict(list)

    def set_captions(self, lang, captions):
        self._captions[lang] = captions
    
    def get_languages(self):
        return self._captions.keys()

    def get_captions(self, lang):
        return self._captions[lang]

    def add_style(self, id, style):
        self._styles[id] = style

    def get_styles(self):
        return self._styles.items()

    def is_empty(self):
        return all([len(captions) == 0 for captions in self._captions.values()])


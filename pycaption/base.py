from collections import defaultdict
from datetime import timedelta


DEFAULT_LANGUAGE_CODE = u'en-US'


def force_byte_string(content):
    try:
        return content.encode(u'UTF-8')
    except UnicodeEncodeError:
        raise RuntimeError(u'Invalid content encoding')
    except UnicodeDecodeError:
        return content


class CaptionConverter(object):
    def __init__(self, captions=None):
        self.captions = captions if captions else []

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
    def __init__(self, *args, **kwargs):
        pass

    def detect(self, content):
        if content:
            return True
        else:
            return False

    def read(self, content):
        return CaptionSet()


class BaseWriter(object):
    def __init__(self, *args, **kwargs):
        pass

    def write(self, content):
        return content


class Style(object):
    def __init__(self):
        pass


class CaptionNode(object):
    """
    A single node within a caption, representing either
    text, a style, or a linebreak.
    """

    TEXT = 1
    STYLE = 2
    BREAK = 3

    def __init__(self, type):
        self.type = type
        self.content = None
        self.start = None

    def __repr__(self):
        t = self.type

        if t == CaptionNode.TEXT:
            return repr(self.content)
        elif t == CaptionNode.BREAK:
            return repr(u'BREAK')
        elif t == CaptionNode.STYLE:
            return repr(u'STYLE: %s %s' % (self.start, self.content))
        else:
            raise RuntimeError(u'Unknown node type: ' + unicode(t))

    @staticmethod
    def create_text(text):
        data = CaptionNode(CaptionNode.TEXT)
        data.content = text
        return data

    @staticmethod
    def create_style(start, content):
        data = CaptionNode(CaptionNode.STYLE)
        data.content = content
        data.start = start
        return data

    @staticmethod
    def create_break():
        return CaptionNode(CaptionNode.BREAK)


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

    def format_start(self, msec_separator=None):
        """
        Format the start time value in milliseconds into a string
        value suitable for some of the supported output formats (ex.
        SRT, DFXP).
        """
        return self._format_timestamp(self.start, msec_separator)

    def format_end(self, msec_separator=None):
        """
        Format the end time value in milliseconds into a string value suitable
        for some of the supported output formats (ex. SRT, DFXP).
        """
        return self._format_timestamp(self.end, msec_separator)

    def __repr__(self):
        return repr(u'%s --> %s\n%s' % (
                self.format_start(), self.format_end(), self.get_text()))

    def get_text(self):
        """
        Get the text of the caption.
        """
        def get_text_for_node(node):
            if node.type == CaptionNode.TEXT:
                return node.content
            if node.type == CaptionNode.BREAK:
                return u'\n'
            return u''
        text_nodes = [get_text_for_node(node) for node in self.nodes]
        return u''.join(text_nodes).strip()

    def _format_timestamp(self, value, msec_separator=None):
        datetime_value = timedelta(milliseconds=(int(value / 1000)))

        str_value = unicode(datetime_value)[:11]
        if not datetime_value.microseconds:
            str_value += u'.000'

        if msec_separator is not None:
            str_value = str_value.replace(u".", msec_separator)

        return u'0' + str_value


class CaptionSet(object):
    """
    A set of captions in potentially multiple languages,
    all representing the same underlying content.
    """
    def __init__(self):
        self._styles = {}

        # Captions by language.
        self._captions = defaultdict(list)

    def set_captions(self, lang, captions):
        self._captions[lang] = captions

    def get_languages(self):
        return self._captions.keys()

    def get_captions(self, lang):
        return self._captions.get(lang, [])

    def add_style(self, id, style):
        self._styles[id] = style

    def get_style(self, style):
        return self._styles.get(style, [])

    def get_styles(self):
        return self._styles.items()

    def set_styles(self, styles):
        self._styles = styles

    def is_empty(self):
        return all(
            [len(captions) == 0 for captions in self._captions.values()]
        )

    def adjust_caption_timing(self, offset=0, rate_skew=1.0):
        """
        Adjust the timing according to offset and rate_skew.
        Skew is applied first, then offset.

        e.g. if skew == 1.1, and offset is 5, a caption originally
        displayed from 10-11 seconds would instead be at 16-17.1
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = []
            for caption in captions:
                caption.start = caption.start * rate_skew + offset
                caption.end = caption.end * rate_skew + offset
                if caption.start >= 0:
                    out_captions.append(caption)
            self.set_captions(lang, out_captions)

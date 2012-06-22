class CaptionConverter():
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


class BaseReader():
    def detect(self, content):
        if content:
            return True
        else:
            return False

    def read(self, content):
        return {'captions': {'en': []}, 'styles': {}}


class BaseWriter():
    def write(self, content):
        return content

import datetime
import re
import logging
from collections import deque
from HTMLParser import HTMLParser

import requests
import cssutils
import nltk
from bs4 import BeautifulSoup

# fix cssutils logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler()) 
cssutils.log.setLevel(logging.FATAL)


# modified html parser
class SAMICleaner(HTMLParser):
    def __init__(self, *args, **kw):
        HTMLParser.__init__(self, *args, **kw)
        self.sami = ''
        self.line = ''
        self.styles = {}
        self.queue = deque()
        self.langs = {}

    # override the parser's handling of starttags
    def handle_starttag(self, tag, attrs):
        # treat divs as spans
        if tag == 'div':
            tag = 'span'
        # figure out the caption language of P tags
        if tag == 'p':
            lang = None
            for attr in attrs:
                a, b = attr
                # if lang is an attribute of the tag
                if a.lower() == 'lang':
                    lang = b[:2]
                # if the P tag has a class, try and find the language
                elif a.lower() == 'class':
                    if '.%s' % b.lower() in self.styles:
                        lang = self.styles['.%s' % b.lower()]['lang']
            # if no language detected, set it as "none"
            if not lang:
                lang = 'None'
            attrs.append(('lang', lang))
            self.langs[lang] = 1
        # clean-up line breaks
        if tag == 'br':
            self.sami += "<br/>"
        # add tag to queue
        else:
            # if already in queue, first close tags off in LIFO order
            while tag in self.queue:
                closer = self.queue.pop()
                self.sami = self.sami + "</%s>" % closer
            # open new tag in queue
            self.queue.append(tag)
            # add tag with attributes
            for attr in attrs:
                a, b = attr
                tag += ' %s="%s"' % (a.lower(), b)
            self.sami += "<%s>" % tag

    # override the parser's handling of endtags
    def handle_endtag(self, tag):
        # treat divs as spans
        if tag == 'div':
            tag = 'span'
        # close off tags in LIFO order, but only if a matching starting tag in queue
        while tag in self.queue:
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag

    # override the parser's handling of data
    def handle_data(self, data):
        self.sami += data.lstrip()

    # override the parser's feed function
    def feed(self, data):
        # try to find style tag in SAMI
        try:
            self.styles = self._css_to_dfxp(BeautifulSoup(data).find('style').get_text())
        except:
            self.styles = []
        # fix erroneous italics tags
        data = data.replace('<i/>', '<i>')
        # clean the SAMI
        HTMLParser.feed(self, data)
        # close any tags that remain in the queue
        while self.queue != deque([]):
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag
        return self.sami, self.styles, self.langs

    # parse into DFXP format the SAMI's stylesheet
    def _css_to_dfxp(self, css):
        # parse via cssutils modules
        sheet = cssutils.parseString(css)
        dfxp_styles = {}

        for rule in sheet:
            new_style = '<style id="%s"' % rule.selectorText.lower()
            lang = None
            not_empty = False
            # keep any style attributes that are needed
            for prop in rule.style:
                if prop.name == 'text-align':
                    new_style += ' tts:textAlign="%s"' % prop.value
                    not_empty = True
                if prop.name == 'font-size':
                    new_style += ' tts:fontSize="%s"' % prop.value.replace('pt', '')
                    not_empty = True
                if prop.name == 'font-family':
                    new_style += ' tts:fontFamily="%s"' % prop.value
                    not_empty = True
                if prop.name == 'color':
                    new_style += ' tts:color="%s"' % prop.value
                    not_empty = True
                if prop.name == 'lang':
                    lang = prop.value[:2]
            new_style += "/>"
            dfxp_styles[rule.selectorText.lower()] = {'style': new_style, 'lang': '%s' % lang, 'use_in_dfxp': not_empty}
        return dfxp_styles


# SAMI Utility class
class SAMIUtility:
    def __init__(self, sami='', url='', *args, **kw):
        self.sami = sami
        self.styles = ''
        self.langs = {}
        self.transcript = ''

        # if url provided, read in the content
        if url:
            self.sami = requests.get(url).content

        # clean the SAMI and check for errors
        self._clean_sami()

    # read SAMI from url
    def read_url(self, url):
        self.sami = requests.get(url).content
        self._clean_sami()

    # get a transcript from the SAMI
    def get_transcript(self):
        sami_soup = BeautifulSoup(self.sami.replace(' <br/>', ' ').replace('<br/>', ' '))
        transcripts = []
        # loop through languages in SAMI
        for lang in self.langs:
            lang_transcript = '* %s Transcript *\n' % lang.upper()
            # get all p tags matching the language
            p_tags = sami_soup.select('p[lang|=%s]' % lang)
            for p in p_tags:
                # strip text from the p tags
                text = p.get_text().strip()
                # ensure not a blank line
                if text not in [u'\n', '\r', '']:
                    lang_transcript += '%s ' % text.replace('\r\n', ' ')
            # split into sentences via nltk module
            lang_transcript = '\n'.join(nltk.sent_tokenize(lang_transcript))
            transcripts.append(lang_transcript)
        return '\n'.join(transcripts)

    # convert SAMI to DFXP
    def get_dfxp(self):
        sami_soup = BeautifulSoup(self.sami)
        divs = ''
        # create a different div for each language
        for lang in self.langs:
            # select P tags matching the current language
            p_tags = sami_soup.select('p[lang|=%s]' % lang)
            div = ''
            # loop through P tags
            for p in p_tags:
                # ensure P tag is not empty
                if p.get_text() not in [u'\n', '\r', '']:
                    self.line = ''
                    # translate all content from the P tag
                    self._translate_tag(p)
                    div += self.line
            div = '\n    <div xml:lang="%s">%s\n    </div>' % (str(lang), div)
            divs += div
        # create style sheet
        styles = ''
        for style in self.styles:
            if self.styles[style]['use_in_dfxp']:
                styles += '\n      %s' % self.styles[style]['style']
        # check to see if P tags have a style
        if 'p' in self.styles:
            p_style = ' id="p"'
        else:
            p_style = ''
        return '''<tt xmlns="http://www.w3.org/ns/ttml" xml:lang="en">
  <head>
    <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">%s
    </styling>
  </head>
  <body%s>%s
  </body>
</tt>''' % (str(styles), p_style, divs)

    # clean the SAMI file
    def _clean_sami(self):
        # check to see if the SAMI is a bogus HTML file
        if '<!doctype html' in self.sami.lower():
            raise Exception('HTML file?')
        # check to see if there are even captions
        elif 'no closed captioning available' in self.sami.lower():
            raise Exception('No closed captioning available?')
        # call the SAMI cleaner
        cleaner = SAMICleaner()
        self.sami, self.styles, self.langs = cleaner.feed(self.sami)
        # check to see if the file was empty of P tags
        if self.langs == {}:
            raise Exception('Empty file, or invalid "P" tags?')

    # recursively loop through content and deal with tags and text as appropriate
    def _translate_tag(self, tag):
        try:
            # convert line breaks
            if tag.name == 'br':
                self.line += '<br/>\n        '
            # convert italics
            if tag.name == 'i':
                self.line += '%s<span tts:fontStyle="italic">' % ('' if self.line[-1] == ' ' else ' ')
                # recursively call function for any children elements
                for a in tag.contents:
                    self._translate_tag(a)
                self.line += '</span> '
            elif tag.name == 'p':
                # convert tag attributes
                args = self._conv_attrs(tag)
                self.line += '\n      <%s%s>\n        ' % (tag.name, args)
                # recursively call function for any children elements
                for a in tag.contents:
                    self._translate_tag(a)
                self.line += '\n      </%s>' % tag.name
            elif tag.name == 'span':
                # convert tag attributes
                args = self._conv_attrs(tag)
                # only include span tag if attributes returned
                if args != '':
                    self.line += '%s<%s%s>' % (('' if self.line[-1] == ' ' else ' '), tag.name, args)
                    # recursively call function for any children elements
                    for a in tag.contents:
                        self._translate_tag(a)
                    self.line += '</%s> ' % tag.name
                else:
                    logger.warning("Found unsupported tag type: %s" % tag.name)
                    # recursively call function for any children elements
                    for a in tag.contents:
                        self._translate_tag(a)
            else:
                # recursively call function for any children elements
                for a in tag.contents:
                    self._translate_tag(a)
        # if no more tags found, strip text
        except:
            self.line += tag.strip()

    # convert attributes from CSS to DFXP
    def _conv_attrs(self, tag):
        attrs = ''
        css_attrs = tag.attrs
        # if P tag, create start and end times
        if tag.name == 'p':
            attrs += ' begin="%s"' % ('0' + str(datetime.timedelta(milliseconds=(int(tag.parent['start']))))[:11])
            # create end time based on next sync tag
            try:
                attrs += ' end="%s"' % ('0' + str(datetime.timedelta(milliseconds=(int(tag.parent.next_sibling['start']))))[:11])
            # if no more sync tags, create end time based on current start time plus 4 seconds
            except:
                attrs += ' end="%s"' % ('0' + str(datetime.timedelta(milliseconds=(int(tag.parent['start']) + 4000)))[:11])
        # convert CSS styles to DFXP
        for arg in css_attrs:
            if arg == "id":
                attrs += ' id="#%s"' % args[a]
            elif arg == "class" and tag.name != 'p':
                attrs += ' id=".%s"' % args[a][0]
            elif arg == "style":
                styles = css_attrs[arg].split(';')
                for style in styles:
                    style = style.split(':')
                    if style[0] == 'text-align':
                        attrs += ' tts:textAlign="%s"' % style[1].strip()
                    elif style[0] == 'font-family':
                        attrs += ' tts:fontFamily="%s"' % style[1].strip()
                    elif style[0] == 'font-size':
                        attrs += ' tts:fontSize="%s"' % style[1].strip()
                    elif style[0] == 'color':
                        attrs += ' tts:color="%s"' % style[1].strip()
        return attrs

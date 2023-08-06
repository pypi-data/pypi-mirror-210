"""HTML file indexer"""
import datetime
import re
import html.parser

from metaindex import logger
from metaindex.shared import DUBLINCORE_TAGS
from metaindex.indexer import IndexerBase, only_if_changed


class HTMLIndexer(IndexerBase):
    """HTML file indexer"""
    NAME = 'html'
    ACCEPT = ['text/html', '.html', '.htm']
    PREFIX = ('html',)

    @only_if_changed
    def run(self, path, metadata, _):
        logger.debug('[%s] processing %s', self.NAME, path)
        metaparser = MetadataExtractor(metadata)
        metaparser.feed(path.read_text())


def get_datetime(value):
    """Try to extract a date (YYYY[-MM[-DD]]) and a time from value

    Returns a tuple (date, time), either of which may be None
    """
    formats = [(re.compile(r'^([0-9]{4})'), lambda t: t[0]),
               (re.compile(r'^([0-9]{4}-[01][0-9])'), lambda t: t[0]),
               (re.compile(r'^([0-9]{4}-[01][0-9]-[0-2][0-9])'), lambda t: t[0]),
               (re.compile(r'^([0-9]{4})-([01][0-9])-([0-3][0-9])T([0-2][0-9]):([0-5][0-9]):([0-6][0-9])'),
                lambda t: datetime.datetime(*[int(v) for v in t])),
              ]
    date = None
    time = None

    for pattern, fnc in reversed(formats):
        match = pattern.match(value)
        if match is None:
            continue

        try:
            date = fnc(match.groups())

            if isinstance(date, datetime.datetime):
                time = date.time()
                date = date.date()
            break
        except ValueError:
            continue

    return date, time


class MetadataExtractor(html.parser.HTMLParser):
    """HTML parser that extracts metadata from meta tags"""
    PREFIX = HTMLIndexer.PREFIX[0] + '.'

    def __init__(self, metadata, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = metadata

    def handle_starttag(self, tag, attrs):
        if tag != 'meta':
            return
        name = ''
        content = ''
        for key, value in attrs:
            if not isinstance(value, str):
                continue
            if key == 'name':
                name = value
            if key == 'content':
                content = value

        if len(name) == 0 or len(content) == 0:
            return

        if name in ['author', 'description', 'creator', 'publisher']:
            self.metadata.add(self.PREFIX + name, content)

        elif name == 'keywords':
            for keyword in content.split(','):
                self.metadata.add(self.PREFIX + 'keyword', keyword)

        elif name.lower().startswith('dc.') and \
             name.lower()[3:] in DUBLINCORE_TAGS:
            tagname = name.lower()[3:]
            if tagname == 'date':
                date, time = get_datetime(content)
                if date is not None:
                    self.metadata.add(self.PREFIX + 'date', date)
                if time is not None:
                    self.metadata.add(self.PREFIX + 'time', time)
            else:
                self.metadata.add(self.PREFIX + name.lower()[3:], content)

"""Filename based indexer"""
import datetime
import re

from metaindex import logger
from metaindex.indexer import IndexerBase


class FileTagsIndexer(IndexerBase):
    """Filename based indexer"""
    NAME = 'filetags'
    ACCEPT = '*'
    PREFIX = 'filetags'

    TAG_MARKER = ' -- '
    DATE_PATTERN = (re.compile(r'^([0-9]+)-([01][0-9])-([0-3][0-9])'), 10, datetime.date)
    DATE2_PATTERN = (re.compile(r'^([0-9]+)([01][0-9])([0-3][0-9])'), 8, datetime.date)
    DATETIME_PATTERN = (re.compile(r'^([0-9]+)-([01][0-9])-([0-3][0-9])[T_]'
                                   r'([0-2][0-9])[._-]([0-6][0-9])'), 16,
                        datetime.datetime)
    DATETIME2_PATTERN = (re.compile(r'^([0-9]+)([01][0-9])([0-3][0-9])_'
                                    r'([0-2][0-9])([0-6][0-9])'), 13,
                         datetime.datetime)
    DATETIMESEC_PATTERN = (re.compile(r'^([0-9]+)-([01][0-9])-([0-3][0-9])[T_]'
                                      r'([0-2][0-9])[._-]([0-6][0-9])[._-]'
                                      r'([0-6][0-9])'), 19,
                           datetime.datetime)
    DATETIMESEC2_PATTERN = (re.compile(r'^([0-9]+)([01][0-9])([0-3][0-9])_'
                                       r'([0-2][0-9])([0-6][0-9])([0-6][0-9])'),
                                       15,
                            datetime.datetime)
    DCR_DATE1_PATTERN = (re.compile(r'^IMG_([0-9]{4})([01][0-9])([0-3][0-9])'), 12,
                         datetime.date)
    DCR_DATETIME1_PATTERN = (re.compile(r'^IMG_([0-9]{4})([01][0-9])([0-3][0-9])_'
                                        r'([0-2][0-9])([0-5][0-9])([0-6][0-9])'),
                             19, datetime.datetime)
    ALL_DT_PATTERNS = list(sorted([
                        DATE_PATTERN,
                        DATE2_PATTERN,
                        DATETIME_PATTERN,
                        DATETIME2_PATTERN,
                        DATETIMESEC_PATTERN,
                        DATETIMESEC2_PATTERN,
                        DCR_DATE1_PATTERN,
                        DCR_DATETIME1_PATTERN,
                        ], key=lambda p: p[1], reverse=True))

    def run(self, path, metadata, _):
        logger.debug(f"[filetags] Running {path.stem}")
        result = set()

        _, result = self.extract_metadata(path.stem)

        if path.parent != path:
            # if possible, extract some metadata from the path this file is in
            path = path.parent

            success, tags = self.extract_metadata(path.stem)
            if success:
                result |= {(tag, value)
                           for tag, value in tags
                           if tag in [self.NAME + '.date', self.NAME + '.tag', self.NAME + '.time']}

        for key, value in result:
            metadata.add(key, value)

    def extract_metadata(self, text):
        result = set()
        tags = None

        match, text = self.obtain_datetime(text)

        if match:
            if isinstance(match, datetime.datetime):
                result.add((self.PREFIX + '.date', match.date()))
                result.add((self.PREFIX + '.time', match.time()))
            else:
                result.add((self.PREFIX + '.date', match))

        # date is a range in the form of YYYY-MM-DD--<some date>
        if match and text.startswith('--'):
            rangeend, text = self.obtain_datetime(text[2:])
            # TODO: do something useful with rangeend

        # find the TAG_MARKER, usually ' -- ', to auto specify tags/subject
        if self.TAG_MARKER in text:
            text, tags = text.split(self.TAG_MARKER, 1)
            result |= {(self.PREFIX + '.tag', tag) for tag in tags.split()}

        if text.startswith('-'):
            text = text[1:]

        if len(text.strip()) > 0 and len(result) > 0:
            # only add the title if anything else was found,
            # otherwise the title is just the filename and that's useless
            # also remove any leading or trailing spaces and underscores and
            # leading dashes
            text = text.lstrip('-').strip('_').strip()
            result.add((self.PREFIX + '.title', text))

        return len(result) > 0, result

    def obtain_datetime(self, text):
        match = None

        for pattern, length, type_ in self.ALL_DT_PATTERNS:
            if len(text) < length:
                continue

            match = pattern.match(text)
            if not match:
                continue

            try:
                match = type_(*[int(value) for value in match.groups()])
                text = text[length:]
                break
            except (ValueError, OverflowError):
                match = None
                continue

        return match, text

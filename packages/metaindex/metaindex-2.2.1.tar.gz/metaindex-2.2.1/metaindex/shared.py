"""Functions, names, and identifiers shared in the code"""
import codecs
import re
import datetime
from pathlib import Path

EXTRA = 'extra.'
IS_RECURSIVE = 'extra_metadata_is_recursive'
LAST_MODIFIED = 'extra_metadata_last_modified'
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_RE = re.compile(r'^([0-9]{4})-([01][0-9])-([0-3][0-9])$')
TIME_RE = re.compile(r'^([0-2][0-9]):([0-5][0-9])(?::([0-6][0-9]))?$')

DUBLINCORE_TAGS = {
    'contributor',
    'coverage',
    'creator',
    'date',
    'description',
    'format',
    'identifier',
    'language',
    'publisher',
    'relation',
    'rights',
    'source',
    'subject',
    'title',
    'type',
}


def get_last_modified(file_):
    """Return the last_modified datetime of the given file.

    This will drop the microsecond part of the timestamp! The reasoning is that
    last_modified will be taken during database cache updates. If a change
    happens at the same second to a file, just after the indexer passed it,
    there's probably a good chance the file gets modified again in the near
    future at which point the indexer will pick up the change.
    Other than that, the cache can forcefully be cleared, too.
    """
    return datetime.datetime.fromtimestamp(file_.stat().st_mtime).replace(microsecond=0)


def strfdt(timestamp):
    """Return the strftime'd timestamp

    This function will also ensure that the returned value has the correct
    amount of leading zeroes, for example when the datetime should be 0001-01-01.
    """
    text = timestamp.strftime(TIMESTAMP_FORMAT)
    return "0"*max(0, 15-len(text)) + text


def strpdt(text):
    return datetime.datetime.strptime(text, TIMESTAMP_FORMAT)


def find_files(paths, recursive=True, ignore_dirs=None):
    """Find all files in these paths"""
    if not isinstance(paths, list):
        paths = [paths]
    if ignore_dirs is None:
        ignore_dirs = []

    pathqueue = list(paths)
    filenames = []

    while len(pathqueue) > 0:
        path = pathqueue.pop(0)

        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            continue

        for item in path.iterdir():
            if item.is_dir() and recursive and item.parts[-1] not in ignore_dirs:
                pathqueue.append(item)
                continue

            if item.is_file():
                filenames.append(item)

    return filenames


def make_mount_relative(path):
    """Return the path relative to its mount point

    For example, a file ``/mnt/EXTHD/doc.pdf`` would return ``/doc.pdf``
    if ``/mnt/EXTHD`` is the mount point.
    """
    path = path.resolve()
    devid = path.stat().st_dev

    # not a mount point at all
    if Path(path.parts[0]).stat().st_dev == devid:
        return path

    parts = [path.name]
    path = path.parent

    while path.parent != path and path.stat().st_dev == devid:
        parts.insert(0, path.name)
        path = path.parent

    # The 'root' of the mount point, eg. 'EXTHD' should not be
    # part of the relative path
    path = Path(*(parts[1:]))
    return path


def jsonify(that):
    """Return ``that`` in a form that can be exported as JSON"""
    if isinstance(that, datetime.datetime):
        return strfdt(that)

    if isinstance(that, datetime.date):
        text = that.strftime("%Y-%m-%d")
        return "0"*(max(0, 8-len(text)))+text

    if isinstance(that, datetime.time):
        text = that.strftime("%H:%M:%S")
        return text

    if isinstance(that, dict):
        return {jsonify(k): jsonify(v)
                for k, v in that.items()}

    if isinstance(that, (tuple, set, list)):
        return [jsonify(v) for v in that]

    if isinstance(that, Path):
        return str(that)

    return that


def merge_date_time(entries):
    """Given a metadata dict with 'date' and 'extra.time', merge them

    This function is supposed to be used on sidecar files where the 'extra.date'
    is saved as 'date: ...'.

    Returns the (potentially modified) dict ``entries``
    """
    date_match = DATE_RE.match(entries.get('date', ''))
    time_match = TIME_RE.match(entries.get('time', ''))

    if date_match is not None and time_match is not None:
        del entries['time']
        date_match = list(date_match.groups())
        time_match = list(time_match.groups())
        if time_match[2] is None:
            time_match[2] = '0'
        entries['date'] = '{}-{}-{} {}:{}:{}'.format(*date_match, *time_match)

    return entries


def split_date_time(entry):
    """Given a CacheEntry with a 'extra.date' field, attempt to split that into 'date' and 'time'

    Returns ``entry`` for convenience, but modifies ``entry`` in place.
    """
    timestamps = entry.get(EXTRA + 'date')
    for timestamp in timestamps:
        try:
            text = timestamp.raw_value
            if len(text) == 16:
                # it’s too short, but maybe just doesn’t have the seconds
                text += ':00'
            dt = strpdt(text)
            entry.delete((EXTRA + 'date', timestamp))
            entry.add(EXTRA + 'date', dt.date())
            entry.add(EXTRA + 'time', dt.time())
        except ValueError:
            continue
    return entry


def to_utf8(raw):
    """Decode a blob of bytes into a UTF-8 string
    
    Attempts to determine the encoding automatically
    """
    if isinstance(raw, str):
        return raw
    encoding = None
    skip = 1

    if raw.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8'
    elif raw.startswith(codecs.BOM_UTF16_BE):
        encoding = 'utf-16-be'
    elif raw.startswith(codecs.BOM_UTF16_LE):
        encoding = 'utf-16-le'
    elif raw.startswith(codecs.BOM_UTF32_BE):
        encoding = 'utf-32-be'
    elif raw.startswith(codecs.BOM_UTF32_LE):
        encoding = 'utf-32-le'
    else:
        # just best efford
        encoding = 'utf-8'
        skip = 0

    try:
        text = str(raw, encoding=encoding).strip()
        return text[skip:]  # drop the BOM, if applicable
    except UnicodeError:
        pass
    return None

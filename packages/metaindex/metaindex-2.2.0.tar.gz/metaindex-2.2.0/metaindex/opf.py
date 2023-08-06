import pathlib
import datetime

from metaindex import shared
from metaindex.cacheentry import CacheEntry
from metaindex.xmlproxy import etree, check_defusedxml


SUFFIX = '.opf'


def get(metadatafile):
    if isinstance(metadatafile, (str, pathlib.Path)):
        with open(metadatafile, "rt", encoding="utf-8") as fh:
            return get(fh)

    entry = parse_opf(metadatafile.read(), shared.EXTRA)
    if hasattr(metadatafile, 'name'):
        entry.path = pathlib.Path(metadatafile.name)

    return entry


def get_for_collection(metadatafile, basepath=None):
    if isinstance(metadatafile, (str, pathlib.Path)):
        with open(metadatafile, "rt", encoding="utf-8") as fh:
            return get_for_collection(fh, pathlib.Path(metadatafile).parent)

    data = parse_opf(metadatafile.read(), prefix=shared.EXTRA)
    data.path = basepath
    data.add(shared.IS_RECURSIVE, True)

    return {basepath: data}


DT_FORMATS = [('%Y-%m-%dT%H:%M:%S', 19, ''),
              ('%Y-%m-%d', 10, 'date')]


def parse_opf(content, prefix='opf.'):
    check_defusedxml()
    result = CacheEntry(None)

    try:
        root = etree.fromstring(content)
    except:
        return result

    for node in root.findall('.//{http://purl.org/dc/elements/1.1/}*'):
        # tag name will start with {namespace}, get rid of it
        _, tagname = node.tag.split('}', 1)

        text = node.text
        if tagname == 'date':
            for fmt, length, type_ in DT_FORMATS:
                try:
                    text = datetime.datetime.strptime(text[:length], fmt)
                    if type_ == 'date':
                        text = text.date()
                    break
                except ValueError as exc:
                    pass

        tagname = prefix + tagname

        if isinstance(text, datetime.datetime):
            result.add(prefix + 'date', text.date())
            result.add(prefix + 'time', text.time())
        elif isinstance(text, datetime.date):
            result.add(prefix + 'date', text)
        else:
            result.add(tagname, text)

    for node in root.findall('.//{http://www.idpf.org/2007/opf}meta'):
        _, tagname = node.tag.split('}', 1)

        if 'name' not in node.keys() or 'content' not in node.keys():
            continue

        name = node.get('name')
        if name is not None:
            # calibre specific attributes are just handled as if they were native attributes
            if name.startswith('calibre:'):
                _, name = name.split(':', 1)

            # so far only accept these specific attributes from the IDPF (calibre) namespace
            if name in ['series', 'series_index']:
                result.add(prefix + name, node.get('content'))

    return result

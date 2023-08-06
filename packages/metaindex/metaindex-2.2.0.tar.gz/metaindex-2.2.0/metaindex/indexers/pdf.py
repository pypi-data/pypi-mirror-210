"""Various indexers for common formats"""
import io
import datetime

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import PIL
    import PIL.Image
except ImportError:
    PIL = None

from metaindex import logger
from metaindex.indexer import IndexerBase, only_if_changed


if pypdf is not None:
    class PyPdfIndexer(IndexerBase):
        """PYF file indexer using PyPDF"""
        NAME = 'pypdf'
        ACCEPT = ['application/pdf']
        PREFIX = ('pdf', 'ocr')

        PDF_METADATA = ('title', 'author', 'creator', 'producer', 'keywords',
                        'manager', 'status', 'category', 'modification_date',
                        'creation_date', 'subject')

        @only_if_changed
        def run(self, path, info, _):
            logger.debug(f"[pypdf] processing {path.name}")
            should_ocr = self.should_ocr(path)
            should_fulltext = self.should_fulltext(path)

            reader = pypdf.PdfReader(path)

            info.add('pdf.pages', len(reader.pages))

            for key in self.PDF_METADATA:
                if not hasattr(reader.metadata, key):
                    continue
                value = sanitize_pdf_value(getattr(reader.metadata, key))
                if value is None:
                    continue
                if isinstance(value, datetime.datetime):
                    info.add('pdf.date', value.date())
                    info.add('pdf.time', value.time())
                info.add('pdf.' + key.lower(), getattr(reader.metadata, key))

            language = None
            for tag, value in info:
                if not tag.endswith('.language'):
                    continue
                if self.ocr.language_supported(str(value)):
                    language = str(value)
                    logger.debug(f"... assuming language is '{language}'")
                    break

            if not should_fulltext:
                return

            fulltext = ''
            for page in reader.pages:
                text = page.extract_text().strip()
                fulltext += text

                if not should_ocr:
                    # no OCR here
                    continue

                try:
                    # apparently this can fail with 'not enough image data'
                    images = list(page.images)
                except ValueError:
                    images = []

                for image in images:
                    logger.debug(f"... OCR on image {image.name}")
                    blob = io.BytesIO(image.data)
                    try:
                        pilimg = PIL.Image.open(blob)
                        result = self.ocr.run(pilimg, language)

                        if result.success:
                            logger.debug(f" ... found text of {len(result.fulltext)} bytes")
                            fulltext += result.fulltext
                    except PIL.UnidentifiedImageError as exc:
                        logger.debug(f"Unidentified image: {exc}")
                        continue
                    except OSError as exc:
                        logger.debug(f"Failed to run OCR: {exc}")

            info.add('pdf.fulltext', fulltext)


def sanitize_pdf_value(value):
    if value is None:
        return ""

    if isinstance(value, bytes):
        return ""

    return value

"""OCR facilities"""
import shutil
import subprocess
import io

try:
    from PIL import Image
except ImportError:
    Image = None

from metaindex import logger


Tesseract = shutil.which('tesseract')


_fatal_logged = False


class OCRResult:
    """The outcome of an OCR run
    """
    def __init__(self, **kwargs):
        self.exc = kwargs.get('exc', None)
        """An exception that occured during the OCR run"""
        self.success = kwargs.get('success', False)
        """Whether or not the OCR run was successful"""
        self.fulltext = kwargs.get('fulltext', None)
        """The fulltext that was extracted"""
        self.language = kwargs.get('language', None)
        """What language was used for extraction"""
        self.confidence = kwargs.get('confidence', None)
        """The numerical confidence value """

    def __bool__(self):
        return self.success

    def __str__(self):
        return self.fulltext

    def __lt__(self, other):
        return self.comparator() < other.comparator()

    def comparator(self):
        """The values to use for comparisons between OCR results"""
        return [not self.success, self.confidence]


class OCRFacility:
    """API of OCR facilities
    """
    def __init__(self, accept_list=None, **kwargs):
        """:param languages: list of languages to try when running OCR"""
        self.accept_list = accept_list
        self.languages = kwargs.get('languages', ['eng', 'deu'])

    def language_supported(self, language):
        """Check if the language is supported by this OCR

        ``language`` may be a string or a list of languages
        """
        return False

    def run(self, image, lang=None):
        """Execute an OCR run on this image

        If ``lang`` is provided, this language will be used for OCR'ing.
        If not provided ``self.languages`` will be used.

        Returns an instance of OCRResult
        """
        return OCRResult(success=False)


class Dummy(OCRFacility):
    """Dummy OCR facility

    Doesn't do anything, but provides the API.
    """
    def run(self, image, lang=None):
        return OCRResult(success=False)


if Tesseract is None:
    class TesseractOCR(OCRFacility):
        def run(self, image, language=None):
            global _fatal_logged
            if not _fatal_logged:
                logger.fatal("Tesseract is not installed. Cannot run OCR")
                _fatal_logged = True
            return super().run(image)

else:
    class TesseractOCR(OCRFacility):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.supported_languages = None

        def run(self, image, language=None):
            langs = self.languages[:]
            if language is not None:
                langs = [language]
            results = [self.do_run(image, lang) for lang in langs]
            best = OCRResult(success=False)
            if len(results) > 0:
                results.sort()
                best = results[0]
            return best

        def language_supported(self, language):
            if self.supported_languages is None:
                process = subprocess.run([Tesseract, '--list-langs'],
                                         capture_output=True,
                                         check=False)
                if process.returncode == 0:
                    lines = str(process.stdout, 'utf-8').split("\n")
                    self.supported_languages = [l.strip()
                                                for l in lines
                                                if len(l.strip()) > 0][1:]
                else:
                    logger.error("Could not determine tesseracts supported languages")
                    self.supported_languages = []
            return language in self.supported_languages

        def do_run(self, image, lang):
            tess = None
            result = OCRResult(success=False, fulltext='', confidence=0, language=lang)
            try:
                imagedata = io.BytesIO()
                image.save(imagedata, "JPEG")
                imagedata.seek(0)
                process = subprocess.run([Tesseract, '-', '-', '-l', lang],
                                         input=imagedata.getbuffer(),
                                         capture_output=True,
                                         check=False)
                if process.returncode == 0:
                    result.fulltext = str(process.stdout, 'utf-8').strip()
                    result.confidence = 1
                    result.success = True
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                result.exc = exc
            finally:
                if tess is not None:
                    tess.clear()
            return result

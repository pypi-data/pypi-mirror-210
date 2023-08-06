import datetime
import fitz
import logging
import re
from PIL import Image
import os
import sys

from lost_cat.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    """Process a word document"""
    def __init__(self, uri: str = None, bytes_io: bytes = None, settings: dict = None) -> None:
        super().__init__(uri=uri, bytes_io=bytes_io, settings=settings)
        self._version = "0.0.1"
        self._name = f"{self.__class__.__name__.lower()} {self._version}"

        if not settings:
            logger.debug("Loading default settings")
            self.settings = PDFParser.avail_config()

        logger.debug("Name: %s", self._name)
        logger.debug("Settings: %s", self.settings)

        # file
        self._uri = None
        self._file = None
        if uri:
            self._uri = uri
            self._file = fitz.open(self._uri)
        elif bytes_io:
            self._file = fitz.open(stream=bytes_io, filetype="pdf")

    @staticmethod
    def avail_config() -> dict:
        """returns default configuration details about the class"""
        return {
            "options":{},
            "uritypes": ["file"],
            "source":[
                {
                    "table": "URIMD",
                    "key": "ext",
                    "values": [".pdf"]
                }
            ]
        }

    def parser(self) -> dict:
        """will parser the open file and retrn the result"""
        _data = {}
        for _mdk, _mdv in self.get_metadata().items():
            _mdk = self._alias_tags.get(_mdk, _mdk)
            _data[_mdk] = _mdv
        return _data

    def get_toc(self) -> dict:
        """ """
        _data = []
        _data = self._file.get_toc(simple=True)

        return {
            "type": "toc",
            "toc": _data
        }

    def get_content(self) -> dict:
        """Returns the text in the pdf as a dict
        type: "lines"
        pages: text blob organised left to right top to bottom
        lines: list of text lines"""
        _pages = {}
        _lines = []
        for _idx, _page in enumerate(self._file):
            _text = _page.get_text('text', sort=True, flags=2)
            if _text:
                _pages[_idx] = _text
                # the text is split on lines
                _lines.extend([x.strip() for x in _text.split("\n") if x.strip()])

        return {
            "type": "lines",
            "pages": _pages,
            "lines": _lines
        }

    def get_textblocks(self) -> dict:
        """Returns the text in the pdf as a list of
        bounding boxes, text
        types: "blocks"
        pages: dict of lists of pages by pagesidx
        (x0, y0, x1, y1, "lines in the block", block_no, block_type)
        see https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractBLOCKS"""
        _pages = {}
        _lines = []
        for _idx, _page in enumerate(self._file):
            if _blocks := _page.get_text('blocks', sort=True, flags=2):
                _pages[_idx] = _blocks

        return {
            "type": "blocks",
            "pages": _pages
        }

    def get_wordblocks(self) -> dict:
        """Returns the text in the pdf as a list of
        bounding boxes, text
        types: "blocks"
        pages: dict of lists of pages by pagesidx
        (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        see https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractWORDS"""
        _pages = {}
        _lines = []
        for _idx, _page in enumerate(self._file):
            if _words := _page.get_text('words', sort=True, flags=2):
                _pages[_idx] = _words

        return {
            "type": "words",
            "pages": _pages
        }

    def get_metadata(self) -> dict:
        """Will get the metadata fro mthe pdf file, and convert the date is a known format to a datetime object"""
        _data = {}
        for _mdk, _mdv in self._file.metadata.items():
            try:
                if _mdk in ["creationDate", "modDate"]:

                    if _mdv is None or _mdv == "":
                        pass
                    if m := re.compile(r"(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<year>[0-9]{4}) (?P<hour>[0-9]{2}):(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})").match(_mdv):
                        _data[_mdk] = f"{m.group('year')}-{m.group('month'):2}-{m.group('day'):2} {m.group('hour')}:{m.group('min')}:{m.group('sec')}"

                    elif m := re.compile(r"(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2}) (?P<hour>[0-9]{2}):(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})").match(_mdv):
                        _data[_mdk] = f"{m.group('year')}-{m.group('month')}-{m.group('day')} {m.group('hour')}:{m.group('min')}:{m.group('sec')}"

                    elif m:= re.compile(r"D:(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})(?P<hour>[0-9]{2})(?P<min>[0-9]{2})(?P<sec>[0-9]{2})(?P<offset>\-[0-9]{2})'(?P<half>[0-9]{2})'").match(_mdv):
                        _data[_mdk] = f"{m.group('year')}-{m.group('month')}-{m.group('day')} {m.group('hour')}:{m.group('min')}:{m.group('sec')}"

                    elif m := re.compile(r"D:(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})(?P<hour>[0-9]{2})(?P<min>[0-9]{2})(?P<sec>[0-9]{2})Z").match(_mdv):
                        _data[_mdk] = f"{m.group('year')}-{m.group('month')}-{m.group('day')} {m.group('hour')}:{m.group('min')}:{m.group('sec')}"

                    elif m := re.compile(r"D:(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})(?P<hour>[0-9]{2})(?P<min>[0-9]{2})(?P<sec>[0-9]{2})").match(_mdv):
                        _data[_mdk] = f"{m.group('year')}-{m.group('month')}-{m.group('day')} {m.group('hour')}:{m.group('min')}:{m.group('sec')}"

                    else:
                        _data[_mdk] = _mdv
                else:
                    _data[_mdk] = _mdv

            except Exception as ex:
                logger.error("Error Processing %s:%s => %s", _mdk, _mdv, ex)
                _data[_mdk] = _mdv

        return _data

    def make_pdf_images(self, first_page: bool = False, dpi: int=300) -> list:
        """Will return the pages as images"""
        images = []

        for i, pg in enumerate(self._file, start=1):
            pix = pg.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            if first_page is True:
                break

        return images

    def make_pdf_thumbnail(self, first_page: bool = True, size: int=300, use_aspect: bool = False) -> list:
        """Will open the pdf file specified and create a thumbnail for the first
        image_max pages:"""
        images = []
        for i, pg in enumerate(self._file, start=1):
            pix = pg.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # fetch the size
            if use_aspect:
                ratio = (img.width / size)
                width = int(img.width / ratio)
                height = int(img.height / ratio)
            else:
                width = 300
                height = 300

            # resize...
            img = img.resize((width, height))
            images.append(img)
            if first_page is True:
                break

        return images

    def avail_functions(self) -> dict:
        """Returns a dict prointing to the available functions"""
        return {
            "toc": self.get_toc,
            "content": self.get_content,
            "textblocks": self.get_textblocks,
            "metadata": self.get_metadata,
            "parser": self.parser,
            "thumbnails": self.make_pdf_thumbnail,
            "screenshots": self.make_pdf_images,
        }

    def close(self, force: bool = False, block: bool = False, timeout: int = -1):
        """will close the """
        if self._file:
            self._file = None

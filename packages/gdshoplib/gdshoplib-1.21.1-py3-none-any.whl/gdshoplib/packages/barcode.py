from io import BufferedReader, BytesIO

import cv2
import numpy as np
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL.Image import Image
from pyzbar import pyzbar


class Barcode:
    def __init__(self, code, /, type="EAN13"):
        self.code = code
        self.barcode_type = type

    @classmethod
    def read(cls, file):
        if isinstance(file, BufferedReader) or isinstance(file, BytesIO):
            image = cv2.imdecode(np.asarray(bytearray(file.read())), cv2.IMREAD_COLOR)
        elif isinstance(file, bytes):
            image = cv2.imdecode(np.fromstring(file, np.uint8), cv2.IMREAD_COLOR)
        elif isinstance(file, Image):
            image = cv2.cvtColor(np.array(file), cv2.COLOR_RGB2BGR)
        else:
            assert file.exists(), "Переданный файл не существует"
            image = cv2.imread(str(file.resolve()))
        decoded_objects = pyzbar.decode(image)
        for obj in decoded_objects:
            return cls(int(obj.data.decode()), type=obj.type)

    def generate(self):
        result = BytesIO()
        barcode_class = get_barcode_class(self.barcode_type)
        image = barcode_class(str(self.code), writer=ImageWriter())
        image.render().save(result, format="PNG")
        return result.getvalue()

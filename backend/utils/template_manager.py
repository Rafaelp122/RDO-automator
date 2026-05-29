import io
from copy import deepcopy
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from typing import BinaryIO
from .logger import logger


class TemplateManager:
    def __init__(self, file: BinaryIO):
        self.file = file
        self.wb = None
        self.ws_template = None
        self.extracted_images = []

    def load(self):
        try:
            self.wb = load_workbook(self.file)
            self.ws_template = self.wb.active

            self.extracted_images = []
            if hasattr(self.ws_template, "_images"):
                for img in self.ws_template._images:
                    try:
                        img_bytes = img._data()
                        anchor = img.anchor
                        self.extracted_images.append({"bytes": img_bytes, "anchor": anchor})
                    except Exception as e:
                        logger.warning("Nao foi possivel ler uma imagem do template: %s", e)
                self.ws_template._images = []
        except Exception as e:
            logger.exception("Erro ao abrir template Excel")
            raise ValueError(f"O arquivo de template nao e um Excel (.xlsx) valido: {e}")

    def clone_worksheet(self, title: str):
        new_ws = self.wb.copy_worksheet(self.ws_template)
        new_ws.title = title
        for img_info in self.extracted_images:
            try:
                new_img = OpenpyxlImage(io.BytesIO(img_info["bytes"]))
                new_img.anchor = deepcopy(img_info["anchor"])
                new_ws.add_image(new_img)
            except Exception as e:
                logger.warning("Nao foi possivel injetar imagem na aba %s: %s", title, e)
        return new_ws

    def save_to_stream(self, stream: BinaryIO):
        if self.ws_template:
            self.wb.remove(self.ws_template)
        self.wb.save(stream)
        logger.info("Relatorio salvo no stream")

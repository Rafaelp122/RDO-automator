import os
import io
from copy import copy, deepcopy
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from pathlib import Path
from src.app.core.logger import logger

class TemplateManager:
    """Responsável por carregar, clonar e salvar o template Excel com suporte a imagens"""
    
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.wb = None
        self.ws_template = None
        self.extracted_images = []

    def load(self):
        """Carrega o workbook e extrai as imagens com segurança"""
        if not self.template_path.exists() or self.template_path.stat().st_size == 0:
            raise FileNotFoundError(f"Template inválido ou inexistente: {self.template_path}")
        
        try:
            self.wb = load_workbook(str(self.template_path))
            self.ws_template = self.wb.active
            
            # Extraímos as imagens e limpamos a referência original do openpyxl
            # Isso impede que ele tente acessar um arquivo fechado depois
            self.extracted_images = []
            
            if hasattr(self.ws_template, "_images"):
                for img in self.ws_template._images:
                    try:
                        # Extrai os bytes da imagem
                        img_bytes = img._data()
                        # Guarda a âncora (posição)
                        anchor = img.anchor
                        self.extracted_images.append({
                            "bytes": img_bytes,
                            "anchor": anchor
                        })
                    except Exception as e:
                        logger.warning(f"Não foi possível ler uma imagem do template: {e}")
                
                # Esvazia as imagens originais da aba template para evitar crash no save()
                self.ws_template._images = []
                
        except Exception as e:
            logger.exception("Erro ao abrir template Excel")
            raise ValueError(f"O arquivo de template não é um Excel (.xlsx) válido: {e}")

    def clone_worksheet(self, title: str):
        """Cria uma nova aba baseada no template, inserindo imagens recriadas"""
        new_ws = self.wb.copy_worksheet(self.ws_template)
        new_ws.title = title
        
        # Reinjetar as imagens a partir dos bytes armazenados
        for img_info in self.extracted_images:
            try:
                # Criamos um novo objeto de imagem limpo para cada aba
                new_img = OpenpyxlImage(io.BytesIO(img_info["bytes"]))
                new_img.anchor = deepcopy(img_info["anchor"])
                new_ws.add_image(new_img)
            except Exception as e:
                logger.warning(f"Não foi possível injetar imagem na aba {title}: {e}")
                
        return new_ws

    def save(self, output_path: Path):
        """Remove a aba base e salva o arquivo final"""
        if self.ws_template:
            self.wb.remove(self.ws_template)
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
            try:
                output_path.rename(output_path)
            except OSError:
                raise PermissionError(
                    f"O arquivo '{output_path.name}' está aberto. Por favor, feche-o antes de continuar."
                )

        try:
            self.wb.save(str(output_path))
            logger.info(f"Relatório salva com sucesso em: {output_path}")
        except Exception as e:
            logger.exception(f"Erro ao salvar arquivo final: {e}")
            raise

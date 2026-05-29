import io
from .report_builder import WebReportBuilder
from utils.logger import logger


def generate_report(source_bytes: bytes, template_bytes: bytes, config: dict) -> io.BytesIO:
    builder = WebReportBuilder(source_bytes, template_bytes)

    contract = config["contract"]
    mappings = config["mappings"]
    list_separator = config.get("listSeparator", ", ")
    list_connector = config.get("listConnector", " e ")

    logger.info("Gerando relatorio: mes=%d/%d, %d mappings", contract["mes"], contract["ano"], len(mappings))

    output = builder.build(
        contract=contract,
        mappings=mappings,
        list_separator=list_separator,
        list_connector=list_connector,
    )

    logger.info("Relatorio gerado com sucesso")
    return output

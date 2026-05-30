class AppError(Exception):
    """Exceção base para toda a aplicação.

    Atributos:
        status_code: Código HTTP retornado na resposta.
        default_detail: Mensagem de erro padrão usada quando ``detail`` não é informado.
        default_code: Código de erro machine-readable usado pelo frontend.
    """

    status_code: int = 400
    default_detail: str = "Ocorreu um erro na aplicação."
    default_code: str = "application_error"

    def __init__(self, detail: str | None = None, code: str | None = None) -> None:
        """
        Args:
            detail: Mensagem amigável de erro. Se ``None``, usa ``default_detail``.
            code: Código de erro machine-readable. Se ``None``, usa ``default_code``.
        """
        self.detail = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        super().__init__(self.detail)


class InvalidFileExtension(AppError):
    """Status 400: o arquivo enviado não possui a extensão esperada (.xlsx ou .xls)."""

    status_code = 400
    default_detail = "Extensão de arquivo inválida."
    default_code = "invalid_file_extension"


class InvalidConfigError(AppError):
    """Status 400: o JSON de configuração está malformado ou não atende ao schema."""

    status_code = 400
    default_detail = "Configuração inválida."
    default_code = "invalid_config"


class ReportGenerationError(AppError):
    """Status 500: falha interna durante a geração do relatório consolidado."""

    status_code = 500
    default_detail = "Erro na geração do relatório."
    default_code = "report_generation_error"

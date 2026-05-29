class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class InvalidFileExtension(AppError):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidConfigError(AppError):
    def __init__(self, message: str):
        super().__init__(message)


class ReportGenerationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

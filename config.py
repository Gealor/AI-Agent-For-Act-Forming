import logging
from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корневая директория
BASE_DIR = Path(__file__).resolve().parent
ENV_TEMPLATE = BASE_DIR / ".env.template"
ENV_FILE = BASE_DIR / '.env'

class LoggerSettings(BaseModel):
    LOG_DEFAULT_FORMAT: str = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
    level: int = logging.DEBUG
    datefmt: str = "%Y-%m-%d %H:%M:%S"

# Тестовые файлы
class TestFiles(BaseModel):
    REQUISITES_PATH: Path = BASE_DIR / "requisites"
    IMAGE_PATH: Path = REQUISITES_PATH / "file_png.png"
    IMAGE_2_PATH: Path = REQUISITES_PATH / "file_png_2.png"
    DOCX_PATH: Path = REQUISITES_PATH / "file_docx.docx"
    DOCX_2_PATH: Path = REQUISITES_PATH / "file_docx_2.docx"
    PDF_PATH: Path = REQUISITES_PATH / "file_pdf.pdf"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ENV_TEMPLATE, ENV_FILE),
        case_sensitive=False,
        extra="ignore",

    )

    LLM_MODEL_NAME: str
    LLM_URL: str
    LLM_API_KEY: SecretStr

    MAX_CONTEXT_WINDOW: int = 4000
    # Директории для генерации акта
    TYPST_DIR: Path = BASE_DIR / 'typst'
    FILE_PATH: Path = TYPST_DIR / "act.json"
    TEMPLATE_ACT_PATH: Path = TYPST_DIR / "act.typ"
    FINAL_ACT_PATH: Path = TYPST_DIR / "act.pdf"

    test_files: TestFiles = TestFiles()
    logger: LoggerSettings = LoggerSettings()


settings = Settings() # type: ignore
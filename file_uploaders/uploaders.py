import base64
from pathlib import Path
from typing import Any, Dict, Protocol, Type
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader


class BaseFileUploader(Protocol):
    def upload_file(self, file_path: str | Path) -> Dict[str, Any]:
        ...

UPLOADER_DICT: Dict[str, Type[BaseFileUploader]] = {}

def register_uploader_decorator(*suffixes: str):
    def wrapper(class_uploader):
        for suffix in suffixes:
            UPLOADER_DICT[suffix] = class_uploader
        return class_uploader
    return wrapper

@register_uploader_decorator('.png', '.jpg', '.jpeg', '.webp')
class ImageFileUploader:
    def upload_file(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        # Обрабатываем расширения, чтобы отдавать правильный MIME-type
        ext = path.suffix.lower()[1:]
        mime_type = "jpeg" if ext == "jpg" else ext 

        with open(path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
            
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/{mime_type};base64,{image_data}"}
        }

@register_uploader_decorator('.pdf')
class PdfFileUploader:
    def upload_file(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        content = "\n".join([doc.page_content for doc in docs])
        return {"type": "text", "text": f"--- Контент PDF ({path.name}) ---\n{content}"}

@register_uploader_decorator('.txt', '.csv', '.json', '.md')
class TextFileUploader:
    def upload_file(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        loader = TextLoader(str(path), encoding="utf-8")
        docs = loader.load()
        return {"type": "text", "text": f"--- Контент текстового файла ({path.name}) ---\n{docs[0].page_content}"}

@register_uploader_decorator('.docx')
class WordFileUploader:
    def upload_file(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        # Docx2txtLoader отлично подходит для вытаскивания текста из Word
        loader = Docx2txtLoader(str(path))
        docs = loader.load()
        return {"type": "text", "text": f"--- Контент Word документа ({path.name}) ---\n{docs[0].page_content}"}


class FileUploaderFactory:
    """Извлекает загрузчик из реестра UPLOADER_DICT"""
    @staticmethod
    def get_uploader(file_path: str | Path) -> BaseFileUploader:
        ext = Path(file_path).suffix.lower()
        
        # Ищем класс в словаре
        uploader_class = UPLOADER_DICT.get(ext)
        
        if not uploader_class:
            raise ValueError(f"Формат файла '{ext}' пока не поддерживается.")
            
        # Возвращаем СОЗДАННЫЙ ЭКЗЕМПЛЯР класса (добавляем скобки)
        return uploader_class()
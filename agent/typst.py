import json
from pathlib import Path
import subprocess
from typing import Any, Dict

from config import settings


def _prepare_json_for_typst(data: Dict[str, Any], file_path: Path = settings.FILE_PATH):
    with open(file_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Успешно записано в файл! {file_path}")  
    return file_path


def _typst_run(
    data_path: Path | str,
    template_path: Path | str = settings.TEMPLATE_ACT_PATH, 
    output_path: Path | str = settings.FINAL_ACT_PATH,
) -> Path | str:
    command = (
        "typst", "compile", 
        str(template_path), str(output_path),
        "--input", f"data={data_path}"
    
    )
    try:
        print(f"Компиляция отчета с данными из файла {data_path}...")
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e
    else:
        print(f"Файл успешно записан в {output_path}!")

    return output_path

def delete_file(file: Path) -> None:
    file.unlink(missing_ok=True)

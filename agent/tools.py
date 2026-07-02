import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Tuple

from langchain.tools import ToolException, tool
from pydantic import ValidationError

from config import settings
from models.customers_and_bank import Customer, CustomerInput
from models.jobs import Jobs

def _prepare_json_for_typst(data: Dict[str, Any], file_path: Path = settings.FILE_PATH):
    with open(file_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def _typst_run(
    template_path: Path | str = settings.TEMPLATE_ACT_PATH, 
    output_path: Path | str = settings.FINAL_ACT_PATH,
) -> Path | str:
    command = ("typst", "compile", str(template_path), str(output_path))
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
    else:
        print(f"Файл успешно записан в {output_path}!")

    return output_path



@tool()
def generate_pdf_act(customer: CustomerInput, jobs: List[Jobs]) -> Tuple[Customer, List[Jobs], Path | str]:
    """Получение данных о заказчике, запись их в файл и генерация Акта оказанных услуг"""
    try:
        strict_customer = Customer.model_validate(customer.model_dump())
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"].replace("Value error, ", "")
            errors.append(f"Поле '{field}': {message}")

        raise ToolException("Ошибка валидации. Запись не выполнена:\n" + "\n".join(errors)) # чтобы модель поняла, что произошла ошибка лучше делать так.
    
    data = {
        "jobs": [job.model_dump() for job in jobs],
        "customer": strict_customer.model_dump(),
    }

    _prepare_json_for_typst(data=data)
    
    print("Успешно записано в файл!")  

    output_path = _typst_run()
    
    return strict_customer, jobs, output_path
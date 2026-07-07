from pathlib import Path

from typing import List, Tuple

from langchain.tools import ToolException, tool
from pydantic import ValidationError

from agent.agent_graph.error_handling import hard_errors_handling, soft_errors_handling, split_errors
from agent.typst import _prepare_json_for_typst, _typst_run, delete_file
from config import settings
from models.customers_and_bank import Customer, CustomerInput
from models.jobs import Jobs


def validate_customer(customer: CustomerInput) -> Customer:
    try:
        strict_customer = Customer.model_validate(customer.model_dump())
    except ValidationError as e:
        hard, soft = split_errors(e)
        if hard:
            raise ToolException(hard_errors_handling(hard))
        
        raise ToolException(soft_errors_handling(soft))
    return strict_customer



# TODO: добавить поиск найденных аттрибутов по документу (ИНН, БИК, корр.счет, рас.счет и т.д.)
@tool()
def generate_pdf_act(customer: CustomerInput, jobs: List[Jobs]) -> Tuple[Customer, List[Jobs], Path | str]:
    """Получение данных о заказчике, запись их в файл и генерация Акта оказанных услуг"""
    strict_customer = validate_customer(customer)
    data = {
        "jobs": [job.model_dump() for job in jobs],
        "customer": strict_customer.model_dump(),
    }
    json_path = settings.TYPST_DIR / f"{strict_customer.act_filename}.json"
    data_path = _prepare_json_for_typst(data=data, file_path=json_path)
    data_path = data_path.relative_to(settings.TYPST_DIR)

    output_path = settings.TYPST_DIR / f"{strict_customer.act_filename}.pdf"
    output_path = _typst_run(data_path, output_path=output_path)
    
    delete_file(json_path)
    
    return strict_customer, jobs, output_path
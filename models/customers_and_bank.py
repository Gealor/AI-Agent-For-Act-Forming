from itertools import cycle

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from models.exceptions import InvalidBankCurrentAccountFormat, InvalidCorporateAccountFormat, InvalidSignatoryFormatException

class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Модели для LLM
class BankInput(BaseModel):
    name: str
    BIC: str
    current_account: str
    corporate_account: str

class CustomerInput(BaseModel):
    name: str
    INN: str
    signatory: str
    bank: BankInput
    OGRN: str | None = None
    address: str | None = None


# Модели для 
class Bank(BankInput):
    """Банковские реквизиты заказчика"""
    name: str  # наименование банка
    BIC: str  # БИК
    current_account: str  # расчётный счёт
    corporate_account: str  # корреспондентский счёт

    @field_validator("current_account")
    def check_current_account(cls, value, info: ValidationInfo):
        if len(value) != 20:
            raise InvalidBankCurrentAccountFormat(
                "Длина расчетного счета не соответствует заявленной длине (20 знаков). "
                f"Текущая длина: {len(value)}."
            )
        
        if not value.isdigit():
            raise InvalidBankCurrentAccountFormat("Расчетный счет должен содержать только цифры")
        
        bic: str | None = info.data.get('BIC')
        if not bic:
            raise InvalidBankCurrentAccountFormat("БИК не указан для проверки расчетного счета")

        last_three_digit_bic = bic[-3:]
        union_string = last_three_digit_bic + value 
        cycle_coef = cycle((7,1,3))

        total = sum(
            (int(digit)*coef)%10 
            for digit, coef in zip(union_string, cycle_coef)
        )

        if (total % 10) != 0:
            raise InvalidBankCurrentAccountFormat(
                "Некорректный расчетный счет (не прошел контрольную сумму)"
            )
        
        return value
    
    @field_validator("corporate_account")
    def check_corporate_account(cls, value, info: ValidationInfo):
        if len(value) != 20:
            raise InvalidCorporateAccountFormat(
                "Длина корреспондентского счета не соответствует заявленной длине (20 знаков). "
                f"Текущая длина: {len(value)}."
            )
        
        if not value.isdigit():
            raise InvalidCorporateAccountFormat("Расчетный счет должен содержать только цифры")

        if value[:3] != "301":
            raise InvalidCorporateAccountFormat(
                "Корреспондентский счет должен начинаться с '301'." \
                f"Текущее начало: {value[:3]}"
            )
        
        bic: str | None = info.data.get('BIC')
        if not bic:
            raise InvalidCorporateAccountFormat("БИК не указан для проверки корреспондентского счета")
        
        union_string = "0" + bic[4:6] + value
        cycle_coef = cycle((7,1,3))

        total = sum(
            (int(digit)*coef)%10 
            for digit, coef in zip(union_string, cycle_coef)
        )

        if (total % 10) != 0:
            raise InvalidCorporateAccountFormat(
                "Некорректный корреспондентский счет (не прошел контрольную сумму)"
            )

        return value
        

class Customer(CustomerInput):
    """Заказчик"""
    name: str  # полное название юридического лица, например, ООО «Рога и копыта»
    INN: str  # ИНН
    OGRN: str | None = None  # ОГРН или ОГРНИП
    address: str | None = None  # юридический адрес 
    signatory: str  # подписант
    bank: Bank  # банковские реквизиты заказчика

    @field_validator("signatory")
    def check_signatory(cls, value):
        parts = value.strip().split(" ")

        if len(parts) != 2:
            raise InvalidSignatoryFormatException("Подписант должен состоять из двух частей: Фамилия И.О.")
        
        second_part = parts[1].strip().split(".")[:2]
        if len(second_part) != 2:
            raise InvalidSignatoryFormatException("У подписанта должно присутствовать Имя и Отчество")
        
        for elem in second_part:
            if len(elem.strip()) != 1:
                raise InvalidSignatoryFormatException("Имя и Отчество подписанта должно быть сокращено до одной буквы")
        
        return value





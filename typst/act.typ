#import "num2words_ru.typ": num2words
#import "@preview/zero:0.3.3": num, set-group
#set-group(size: 3, separator: sym.space.thin, threshold: 4)

#let act = json("act.json")

#let act_sum = act.jobs.map(job => job.at("price")).sum()

= Акт выполненных работ

#datetime.today().display("[day].[month].[year]")

#table(
  columns: 2,
  stroke: none,
  inset: (left: 0pt),
  [*Исполнитель:*], [ИП Иванов Иван Иванович],
  [*Заказчик:*],    [#act.customer.at("name")]
)

#table(
  columns: 6,
  [№], [Наименование товара], [Ед. изм.], [Кол-во], [Цена, ₽], [Сумма, ₽],
  ..for (index, job) in act.jobs.enumerate() {(
    [
      #align(center)[#(index + 1)]
    ],[
      #job.at("task")
    ], [#align(center)[шт]], [#align(center)[1]], [
      #align(center)[#num(job.at("price"))]
    ],[
      #align(center)[#num(job.at("price"))]
    ]
  )},
)

Общая стоимость выполненных работ, оказанных услуг в российских рублях: #num(act_sum) (#num2words(act_sum)) 00 копеек. Заказчик не имеет претензий по срокам, качеству и объёму товаров и услуг.

#table(
  columns: 2,
  stroke: none,
  inset: (left: 0pt),
  [
    *#act.customer.at("name")*
  ], [
    *ИП Иванов Иван Иванович*
  ], text(
  )[
    ИНН: #act.customer.at("INN")\
    ОГРН: #act.customer.at("OGRN")\
    Юридический адрес: #act.customer.at("address")\
    Банк: #act.customer.at("bank").at("name")\
    БИК: #act.customer.at("bank").at("BIC")\
    Расчетный счет: #act.customer.at("bank").at("current_account")\
    Корр. счет: #act.customer.at("bank").at("corporate_account")\
  ],[
    ИНН: 111111111111\
    ОГРНИП: 111111111111111\
    Р/с: 11111111111111111111\
    Банк: АО "Пупа и Лупа"\
    БИК: 111111111\
    Корр. счет: 11111111111111111111
  ],[
    \
    #text("________________/") #act.customer.at("signatory") /
  ], [
    \
    #text("________________/") Иванов И.И. /
  ]
)

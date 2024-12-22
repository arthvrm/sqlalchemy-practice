from sqlalchemy import Table, Column, Integer, String, MetaData


metadata_obj = MetaData() # об'єкт що передається у всі теблиці/моделі створені на стороні програми щоб мати доступ для взаємодії з ними(таблицями/моделями)


workers_table = Table(                       # створення таблиці
    "workers",                               # назва таблиці
    metadata_obj,                            # оголошення метадати в таблиці/моделі щоб мати доступ до неї з об'єкту metadata_obj
    Column("id", Integer, primary_key=True), # створення стовпця name, type, pk
    Column("username", String),
)
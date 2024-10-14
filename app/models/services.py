from sqlalchemy import Column, Integer, String, Text, Float
from ..extensions import db


class Service(db.Model):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Название услуги
    description = Column(Text, nullable=True)  # Описание услуги
    price = Column(Float, nullable=False)  # Цена услуги
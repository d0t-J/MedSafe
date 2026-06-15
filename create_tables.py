from core.database import engine, Base
from models.user import User
from models.visitor import Visitor
from models.drug_check import DrugCheck

Base.metadata.create_all(bind=engine)
print("Tables created successfully")

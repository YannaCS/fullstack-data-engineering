from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Create base class for declarative models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
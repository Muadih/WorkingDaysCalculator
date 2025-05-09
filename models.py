from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'NATIONAL' or 'CUSTOM'

    def __repr__(self):
        return f"<Holiday(date={self.date}, name={self.name}, type={self.type})>"

def init_db():
    db.create_all()
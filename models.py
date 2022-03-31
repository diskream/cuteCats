from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CatsModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    breed = db.Column(db.String(30))
    img = db.Column(db.LargeBinary())
    name = db.Column(db.String(30))
    description = db.Column(db.TEXT())
    age = db.Column(db.Integer())

    def __repr__(self):
        return f'{self.name}: {self.breed}, {self.age} месяцев.'
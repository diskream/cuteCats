from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import TypeDecorator
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()


class TSVector(TypeDecorator):
    impl = TSVECTOR


def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector('russian', exp)


class CatsModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    breed = db.Column(db.String(30))
    img = db.Column(db.LargeBinary())
    name = db.Column(db.String(30))
    description = db.Column(db.TEXT())
    age = db.Column(db.Integer())

    __ts_vector__ = db.Column(TSVector(), db.Computed(
        "to_tsvector('russian', breed || ' ' || name || ' ' || description || ' ' || age::text)",
        persisted=True))

    __table_args__ = (db.Index('ix_cats_model___ts_vector__', __ts_vector__, postgresql_using='gin'),)

    def __repr__(self):
        return f'{self.name}: {self.breed}, {self.age} месяцев'

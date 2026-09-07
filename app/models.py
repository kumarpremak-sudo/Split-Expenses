import uuid
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='INR')
    pin_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    members = db.relationship('Member', backref='group', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='group', lazy=True, cascade='all, delete-orphan')

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'currency': self.currency,
            'created_at': self.created_at.isoformat(),
            'members': [m.to_dict() for m in self.members],
            'expenses': [e.to_dict() for e in self.expenses],
        }


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    paid_by_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Other')
    split_among = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    paid_by = db.relationship('Member', backref='expenses_paid')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'paid_by_id': self.paid_by_id,
            'paid_by_name': self.paid_by.name if self.paid_by else 'Unknown',
            'amount': self.amount,
            'description': self.description,
            'category': self.category,
            'split_among': json.loads(self.split_among),
            'created_at': self.created_at.isoformat(),
        }

from app.extensions import db
from sqlalchemy.orm import relationship

domainlist_by_group = db.Table(
    'domainlist_by_group',
    db.Column('domainlist_id', db.Integer, db.ForeignKey('domainlist.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    bind_key="pihole"
)

client_by_group = db.Table(
    'client_by_group',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    bind_key="pihole"
)


class Group(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    description = db.Column(db.Text)
    domains = relationship('Domainlist', secondary=domainlist_by_group, back_populates="groups", lazy="dynamic")
    clients = relationship('Client', secondary=client_by_group, back_populates='groups',
                              lazy="dynamic")


class Domainlist(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, nullable=False, default=0)
    domain = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    comment = db.Column(db.Text)
    groups = relationship('Group', secondary=domainlist_by_group, back_populates="domains", lazy="dynamic")


class Client(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    comment = db.Column(db.Text)
    groups = relationship('Group', secondary=client_by_group, back_populates='clients', lazy="dynamic")

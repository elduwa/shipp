from app.extensions import db


class Group(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    description = db.Column(db.Text)
    adlists = db.relationship('AdList', secondary='adlist_by_group', backref=db.backref('groups', lazy="dynamic"),
                              lazy="dynamic")
    domainlists = db.relationship('DomainList', secondary='domainlist_by_group',
                                  backref=db.backref('groups', lazy="dynamic"), lazy="dynamic")
    clients = db.relationship('Client', secondary='client_by_group', backref=db.backref('groups', lazy="dynamic"),
                              lazy="dynamic")


class DomainList(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, nullable=False, default=0)
    domain = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    comment = db.Column(db.Text)


class AdList(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(255), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    comment = db.Column(db.Text)
    date_updated = db.Column(db.Integer)
    number = db.Column(db.Integer, nullable=False, default=0)
    invalid_domains = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=0)


adlist_by_group = db.Table(
    'adlist_by_group',
    db.Column('adlist_id', db.Integer, db.ForeignKey('adlist.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    bind_key="pihole"
)

gravity = db.Table(
    'gravity',
    db.Column('domain', db.String(255), nullable=False),
    db.Column('adlist_id', db.Integer, db.ForeignKey('adlist.id'), nullable=False),
    bind_key="pihole"
)

info = db.Table(
    'info',
    db.Column('property', db.String(255), primary_key=True),
    db.Column('value', db.String(255), nullable=False),
    bind_key="pihole"
)


class DomainAudit(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))


domainlist_by_group = db.Table(
    'domainlist_by_group',
    db.Column('domainlist_id', db.Integer, db.ForeignKey('domainlist.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    bind_key="pihole"
)


class Client(db.Model):
    __bind_key__ = "pihole"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(255), unique=True, nullable=False)
    date_added = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    date_modified = db.Column(db.Integer, nullable=False, default=db.func.strftime('%s', 'now'))
    comment = db.Column(db.Text)


client_by_group = db.Table(
    'client_by_group',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    bind_key="pihole"
)

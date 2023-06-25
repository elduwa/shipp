from app.extensions import db, cipher_suite
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    device_name = db.Column(db.String(64))
    device_configs = db.relationship('DeviceConfig', backref='device', lazy="dynamic")
    policies = db.relationship("Policy", secondary="policy_device_map",
                               backref=db.backref('devices', lazy="dynamic"), lazy="dynamic")

    def get_current_config(self):
        return self.device_configs.filter_by(valid_to=None).first()

    def get_active_policies(self):
        return self.policies.filter_by(active=True).all()

    def insert_device(self):
        db.session.add(self)
        db.session.commit()

    def update_device(self):
        db.session.add(self)
        db.session.commit()

    def delete_device(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Device %r>' % self.mac_address


class DeviceConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    valid_from = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    valid_to = db.Column(db.DateTime, index=True)
    ip_address = db.Column(db.String(39), nullable=False)

    def insert_device_config(self):
        db.session.add(self)
        db.session.commit()

    def update_device_config(self):
        db.session.add(self)
        db.session.commit()

    def delete_device_config(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<DeviceConfig %r>' % self.id


class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_type = db.Column(db.String(64), nullable=False)
    domain = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=True, nullable=False)

    def insert_policy(self):
        db.session.add(self)
        db.session.commit()

    def update_policy(self):
        db.session.add(self)
        db.session.commit()

    def delete_policy(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Policy %r>' % self.id


policy_device_map = db.Table('policy_device_map',
                             db.Column("policy_id", db.Integer, db.ForeignKey('policy.id'), primary_key=True),
                             db.Column("device_id", db.Integer, db.ForeignKey('device.id'), primary_key=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email_address = db.Column(db.String(64))
    api_keys = db.relationship('UserApiKey', backref='user', lazy="dynamic")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def insert_user(self):
        db.session.add(self)
        db.session.commit()

    def update_user(self):
        db.session.add(self)
        db.session.commit()

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


class UserApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    encrypted_api_key = db.Column(db.String(128), nullable=False)

    @property
    def api_key(self):
        decrypted_api_key = cipher_suite.decrypt(self.encrypted_api_key.encode())
        return decrypted_api_key.decode()

    @api_key.setter
    def set_api_key(self, api_key):
        self.encrypted_api_key = cipher_suite.encrypt(api_key.encode())

    def insert_api_key(self):
        db.session.add(self)
        db.session.commit()

    def update_api_key(self):
        db.session.add(self)
        db.session.commit()

    def delete_api_key(self):
        db.session.delete(self)
        db.session.commit()

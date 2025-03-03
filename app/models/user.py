from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for hash
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    _is_active = db.Column('is_active', db.Boolean, default=True)  # Renamed column

    # Relationships
    role = db.relationship('Role', back_populates='users')
    created_dreams = db.relationship('Dream', back_populates='creator', cascade='all, delete-orphan')
    created_milestones = db.relationship('Milestone', back_populates='creator', cascade='all, delete-orphan')
    created_goals = db.relationship('Goal', back_populates='creator', cascade='all, delete-orphan')
    created_tasks = db.relationship('Task', foreign_keys='Task.creator_id', back_populates='creator', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', back_populates='assignee')

    @property
    def is_active(self):
        # For admin users, always return True to prevent lockout
        if self.is_admin():
            return True
        # If _is_active is None (user not found), return False
        return bool(self._is_active)

    @is_active.setter
    def is_active(self, value):
        # Prevent deactivating admin users
        if self.is_admin() and not value:
            return
        self._is_active = bool(value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def is_admin(self):
        return self.role and self.role.name == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 
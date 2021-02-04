from enum import Enum
from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from dsa import db


# different roles a member account can be assigned
class RoleEnum(Enum):
    member = "member"
    contributor = "contributor"
    mobilizer = "mobilizer"
    organizer = "organizer"
    administrator = "administrator"


class MemberRole(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    role = db.Column(db.Enum(RoleEnum))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))


# a member of chapelboro DSA
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256), nullable=True)
    last_name = db.Column(db.String(256), nullable=True)
    username = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256),unique=True,nullable=False)
    _password = db.Column("password",db.String(256),nullable=False)
    roles = db.relationship('MemberRole', backref='member', lazy=True)

    @property
    def user_roles(self):
        return {r.role.value for r in self.roles}

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def check_password(self,value):
        return check_password_hash(self.password, value)

    def save(self):
        db.session.add(self)
        db.session.commit()
        new_user_role = MemberRole(role="member",member_id=self.id)
        db.session.add(new_user_role)
        db.session.commit()
        self.roles.append(new_user_role)
        db.session.commit()
        return

    def has_role(self, role_name:str):
        # basic permissions management
        return role_name in self.user_roles

    def __repr__(self):
        return f"<Member name={self.first_name} email={self.email}>"

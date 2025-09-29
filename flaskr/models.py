"""Database models for Spartan Teamlog."""

from datetime import datetime
from .db import db


class Member(db.Model):
    """Team member model for attendance tracking."""
    
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    checked_in = db.Column(db.Boolean, default=False, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Member {self.first_name} {self.last_name}>'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def full_name(self):
        """Return the full name of the member."""
        return f'{self.first_name} {self.last_name}'
    
    def check_in(self):
        """Mark member as checked in and update timestamp."""
        self.checked_in = True
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def check_out(self):
        """Mark member as checked out and update timestamp."""
        self.checked_in = False
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    def toggle_active_status(self):
        """Toggle the active status of the member."""
        self.active = not self.active
        self.last_updated = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_active_members(cls):
        """Get all active members."""
        return cls.query.filter_by(active=True).all()
    
    @classmethod
    def get_checked_in_members(cls):
        """Get all currently checked-in members."""
        return cls.query.filter_by(checked_in=True, active=True).all()
    
    def to_dict(self):
        """Convert member to dictionary representation."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'position': self.position,
            'active': self.active,
            'checked_in': self.checked_in,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
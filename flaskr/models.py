"""Database models for Spartan Teamlog."""

from datetime import datetime, timezone
from .db import db


class Position(db.Model):
    """Position model for team member roles."""
    
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    
    # Relationship to members
    members = db.relationship('Member', backref='position_obj', lazy=True)
    
    def __repr__(self):
        return f'<Position {self.name}>'
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_default_positions(cls):
        """Create the default positions if they don't exist."""
        default_positions = [
            {'name': 'member', 'description': 'Regular team member'},
            {'name': 'lead', 'description': 'Team lead with additional responsibilities'},
            {'name': 'mentor', 'description': 'Adult Professional who guides others'},
            {'name': 'coach', 'description': 'Team coach providing guidance and training'}
        ]
        
        for pos_data in default_positions:
            existing = cls.query.filter_by(name=pos_data['name']).first()
            if not existing:
                position = cls(name=pos_data['name'], description=pos_data['description'])
                db.session.add(position)
        
        db.session.commit()


class Member(db.Model):
    """Team member model for attendance tracking."""
    
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idhash = db.Column(db.Integer, nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    checked_in = db.Column(db.Boolean, default=False, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Member {self.first_name} {self.last_name}>'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    @property
    def full_name(self):
        """Return the full name of the member."""
        return f'{self.first_name} {self.last_name}'
    
    @property
    def position(self):
        """Return the position name for backward compatibility."""
        return self.position_obj.name if self.position_obj else None
    
    def check_in(self):
        """Mark member as checked in and update timestamp."""
        # Generate timestamp once for consistent timing
        timestamp = datetime.now(timezone.utc)
        
        self.checked_in = True
        self.last_updated = timestamp
        
        # Create CiCo record with same timestamp in same transaction
        cico_record = CiCo(
            member_id=self.id,
            event_type='checkin',
            timestamp=timestamp
        )
        db.session.add(cico_record)
        db.session.commit()
        
    def check_out(self):
        """Mark member as checked out and update timestamp."""
        # Generate timestamp once for consistent timing
        timestamp = datetime.now(timezone.utc)
        
        self.checked_in = False
        self.last_updated = timestamp
        
        # Create CiCo record with same timestamp in same transaction
        cico_record = CiCo(
            member_id=self.id,
            event_type='checkout',
            timestamp=timestamp
        )
        db.session.add(cico_record)
        db.session.commit()
    
    def toggle_active_status(self):
        """Toggle the active status of the member."""
        self.active = not self.active
        self.last_updated = datetime.now(timezone.utc)
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
            'idhash': self.idhash,
            'position': self.position,
            'position_id': self.position_id,
            'active': self.active,
            'checked_in': self.checked_in,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class CiCo(db.Model):
    """Check-In/Check-Out model for tracking member attendance events."""
    
    __tablename__ = 'cico'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # 'checkin' or 'checkout'
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    notes = db.Column(db.String(200), nullable=True)  # Optional notes about the event
    
    # Relationship to member
    member = db.relationship('Member', backref='cico_records', lazy=True)
    
    def __repr__(self):
        return f'<CiCo {self.event_type} for {self.member.full_name if self.member else "Unknown"} at {self.timestamp}>'
    
    def __str__(self):
        return f'{self.event_type.title()} at {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
    
    @property
    def formatted_timestamp(self):
        """Return a formatted timestamp for display."""
        return self.timestamp.strftime("%m/%d/%Y %I:%M %p") if self.timestamp else "Unknown"
    
    @property
    def time_only(self):
        """Return just the time portion of the timestamp."""
        return self.timestamp.strftime("%I:%M %p") if self.timestamp else "Unknown"
    
    @property
    def date_only(self):
        """Return just the date portion of the timestamp."""
        return self.timestamp.strftime("%m/%d/%Y") if self.timestamp else "Unknown"
    
    @classmethod
    def create_record(cls, member_id, event_type, notes=None, timestamp=None):
        """Create a new check-in/check-out record."""
        record = cls(
            member_id=member_id,
            event_type=event_type,
            notes=notes,
            timestamp=timestamp or datetime.now(timezone.utc)
        )
        db.session.add(record)
        db.session.commit()
        return record
    
    @classmethod
    def get_member_records(cls, member_id, limit=None):
        """Get all check-in/out records for a specific member, ordered by timestamp desc."""
        query = cls.query.filter_by(member_id=member_id).order_by(cls.timestamp.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_recent_records(cls, limit=50):
        """Get recent check-in/out records across all members."""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_todays_records(cls):
        """Get all check-in/out records from today."""
        today = datetime.now(timezone.utc).date()
        return cls.query.filter(
            db.func.date(cls.timestamp) == today
        ).order_by(cls.timestamp.desc()).all()
    
    def to_dict(self):
        """Convert record to dictionary representation."""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'member_name': self.member.full_name if self.member else "Unknown",
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'formatted_timestamp': self.formatted_timestamp,
            'notes': self.notes
        }


# CiCo records are now created directly in Member.check_in() and Member.check_out() methods
# This ensures consistent timestamps and atomic database transactions

        
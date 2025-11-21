"""
Tests for database models and functionality.
"""

import pytest
from datetime import datetime
from flaskr.db import db
from flaskr.models import Member, Position


class TestPosition:
    """Tests for Position model."""
    
    def test_position_creation(self, app):
        """Test creating a position."""
        with app.app_context():
            position = Position(name='test_position', description='Test position')
            db.session.add(position)
            db.session.commit()
            
            assert position.id is not None
            assert position.name == 'test_position'
            assert position.description == 'Test position'
    
    def test_position_string_representation(self, app, sample_positions):
        """Test position string methods."""
        with app.app_context():
            position = sample_positions['member']
            assert str(position) == 'member'
            assert repr(position) == '<Position member>'
    
    def test_create_default_positions(self, app):
        """Test that default positions are created correctly."""
        with app.app_context():
            Position.query.delete()  # Clear existing positions
            db.session.commit()
            
            Position.create_default_positions()
            
            positions = Position.query.all()
            assert len(positions) == 4
            
            names = [pos.name for pos in positions]
            assert 'member' in names
            assert 'lead' in names
            assert 'mentor' in names
            assert 'coach' in names


class TestMember:
    """Tests for Member model."""
    
    def test_member_creation(self, app, sample_positions):
        """Test creating a member."""
        with app.app_context():
            member = Member(
                first_name='Test',
                last_name='User',
                idhash=Member.hash_id('99999'),
                position_id=sample_positions['member'].id
            )
            db.session.add(member)
            db.session.commit()
            
            assert member.id is not None
            assert member.first_name == 'Test'
            assert member.last_name == 'User'
            assert member.active is True  # Default value
            assert member.checked_in is False  # Default value
            assert member.last_updated is not None
    
    def test_member_properties(self, app, sample_member, sample_positions):
        """Test member property methods."""
        with app.app_context():
            member = Member.query.get(sample_member)
            
            assert member.full_name == 'John Doe'
            assert member.position == 'member'
            assert str(member) == 'John Doe'
            assert repr(member) == '<Member John Doe>'
    
    def test_member_check_in(self, app, sample_member):
        """Test member check-in functionality."""
        with app.app_context():
            member = Member.query.get(sample_member)
            
            # Initially not checked in
            assert member.checked_in is False
            
            # Check in
            old_updated = member.last_updated
            member.check_in()
            
            assert member.checked_in is True
            assert member.last_updated > old_updated
    
    def test_member_check_out(self, app, sample_member):
        """Test member check-out functionality."""
        with app.app_context():
            member = Member.query.get(sample_member)
            
            # Check in first
            member.check_in()
            assert member.checked_in is True
            
            # Then check out
            old_updated = member.last_updated
            member.check_out()
            
            assert member.checked_in is False
            assert member.last_updated >= old_updated
    
    def test_toggle_active_status(self, app, sample_member):
        """Test toggling member active status."""
        with app.app_context():
            member = Member.query.get(sample_member)
            
            # Initially active
            assert member.active is True
            
            # Toggle to inactive
            member.toggle_active_status()
            assert member.active is False
            
            # Toggle back to active
            member.toggle_active_status()
            assert member.active is True
    
    def test_get_active_members(self, app, multiple_members):
        """Test getting active members."""
        with app.app_context():
            # All members should be active initially
            active_members = Member.get_active_members()
            assert len(active_members) >= 4
            
            # Deactivate one member
            member = Member.query.get(multiple_members[0])
            member.active = False
            db.session.commit()
            
            # Should have one less active member
            active_members = Member.get_active_members()
            assert len(active_members) >= 3
            assert member not in active_members
    
    def test_get_checked_in_members(self, app, multiple_members):
        """Test getting checked-in members."""
        with app.app_context():
            # Initially no one checked in
            checked_in = Member.get_checked_in_members()
            assert len([m for m in checked_in if m.id in multiple_members]) == 0
            
            # Check in some members
            member1 = Member.query.get(multiple_members[0])
            member2 = Member.query.get(multiple_members[1])
            
            member1.check_in()
            member2.check_in()
            
            checked_in = Member.get_checked_in_members()
            checked_in_ids = [m.id for m in checked_in]
            
            assert member1.id in checked_in_ids
            assert member2.id in checked_in_ids
    
    def test_to_dict(self, app, sample_member):
        """Test member dictionary conversion."""
        with app.app_context():
            member = Member.query.get(sample_member)
            member_dict = member.to_dict()
            
            assert member_dict['id'] == member.id
            assert member_dict['first_name'] == 'John'
            assert member_dict['last_name'] == 'Doe'
            assert member_dict['full_name'] == 'John Doe'
            assert member_dict['position'] == 'member'
            assert member_dict['active'] is True
            assert member_dict['checked_in'] is False
            assert 'last_updated' in member_dict
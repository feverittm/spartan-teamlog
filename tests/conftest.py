"""
Test configuration and fixtures for Spartan Teamlog tests.
"""

import pytest
import tempfile
import os
from flaskr import create_app
from flaskr.db import db, init_db
from flaskr.models import Member, Position


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-key'
    })
    
    with app.app_context():
        init_db()
        # Create default positions for testing
        Position.create_default_positions()
        
    yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_positions(app):
    """Create sample positions for testing."""
    with app.app_context():
        positions = {
            'member': Position.query.filter_by(name='member').first(),
            'lead': Position.query.filter_by(name='lead').first(),
            'mentor': Position.query.filter_by(name='mentor').first(),
            'coach': Position.query.filter_by(name='coach').first()
        }
    return positions


@pytest.fixture
def sample_member(app, sample_positions):
    """Create a sample member for testing."""
    with app.app_context():
        member = Member(
            first_name='John',
            last_name='Doe',
            position_id=sample_positions['member'].id,
            active=True
        )
        db.session.add(member)
        db.session.commit()
        
        # Return the member ID for use in tests
        member_id = member.id
        
    return member_id


@pytest.fixture 
def multiple_members(app, sample_positions):
    """Create multiple sample members for testing."""
    with app.app_context():
        members_data = [
            {'first_name': 'Jane', 'last_name': 'Smith', 'position': 'lead'},
            {'first_name': 'Bob', 'last_name': 'Wilson', 'position': 'mentor'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'position': 'member'},
            {'first_name': 'Charlie', 'last_name': 'Brown', 'position': 'coach'}
        ]
        
        created_members = []
        for data in members_data:
            member = Member(
                first_name=data['first_name'],
                last_name=data['last_name'],
                position_id=sample_positions[data['position']].id,
                active=True
            )
            db.session.add(member)
            db.session.commit()
            created_members.append(member.id)
            
    return created_members
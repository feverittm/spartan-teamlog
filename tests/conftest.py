"""
Test configuration and fixtures for Spartan Teamlog tests.
"""

import pytest
from flaskr import create_app
from flaskr.db import db, init_db
from flaskr.models import Member, Position


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use in-memory database
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-key'
    })

    with app.app_context():
        init_db()
        # Create default positions for testing
        Position.create_default_positions()

    yield app

    # No cleanup needed for in-memory database
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
            idhash=Member.hash_id('12345'),
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
            {'first_name': 'Jane', 'last_name': 'Smith', 'position': 'lead', 'idhash': '67890'},
            {'first_name': 'Bob', 'last_name': 'Wilson', 'position': 'mentor', 'idhash': '11111'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'position': 'member', 'idhash': '22222'},
            {'first_name': 'Charlie', 'last_name': 'Brown', 'position': 'coach', 'idhash': '33333'}
        ]
        
        created_members = []
        for data in members_data:
            member = Member(
                first_name=data['first_name'],
                last_name=data['last_name'],
                idhash=Member.hash_id(data['idhash']),
                position_id=sample_positions[data['position']].id,
                active=True
            )
            db.session.add(member)
            db.session.commit()
            created_members.append(member.id)
            
    return created_members
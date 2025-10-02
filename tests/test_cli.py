"""
Tests for CLI commands.
"""

import pytest
from flaskr.models import Member, Position


def test_init_db_command(runner, app):
    """Test the init-db CLI command."""
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Initialized the database with default positions.' in result.output
    
    # Verify positions were created
    with app.app_context():
        positions = Position.query.all()
        assert len(positions) == 4
        
        position_names = [pos.name for pos in positions]
        expected_names = ['member', 'lead', 'mentor', 'coach']
        for name in expected_names:
            assert name in position_names


def test_seed_db_command(runner, app):
    """Test the seed-db CLI command."""
    result = runner.invoke(args=['seed-db'])
    assert result.exit_code == 0
    assert 'Added 10 sample members to the database.' in result.output
    
    # Verify members were created
    with app.app_context():
        members = Member.query.all()
        assert len(members) == 10
        
        # Check some specific members from seed data
        john = Member.query.filter_by(first_name='John', last_name='Doe').first()
        assert john is not None
        assert john.position == 'lead'
        
        sarah = Member.query.filter_by(first_name='Sarah', last_name='Johnson').first()
        assert sarah is not None
        assert sarah.position == 'lead'
        
        charlie = Member.query.filter_by(first_name='Charlie', last_name='Brown').first()
        assert charlie is not None
        assert charlie.position == 'coach'


def test_seed_db_creates_positions_if_missing(runner, app):
    """Test that seed-db creates positions if they don't exist."""
    # Clear positions first
    with app.app_context():
        Position.query.delete()
        Member.query.delete()
        from flaskr.db import db
        db.session.commit()
    
    result = runner.invoke(args=['seed-db'])
    assert result.exit_code == 0
    
    # Verify positions were created
    with app.app_context():
        positions = Position.query.all()
        assert len(positions) == 4
        
        members = Member.query.all()
        assert len(members) == 10
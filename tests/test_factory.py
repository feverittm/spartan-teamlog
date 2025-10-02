"""
Tests for Flask application factory and configuration.
"""

import pytest
from flaskr import create_app


def test_config():
    """Test that the app can be created with test configuration."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello_route(client):
    """Test the hello route works."""
    response = client.get('/hello')
    assert response.status_code == 200
    assert b'Hello, World!' in response.data


def test_app_creation():
    """Test that app factory creates app correctly."""
    app = create_app({'TESTING': True})
    assert app is not None
    assert app.testing is True


def test_database_initialization(app):
    """Test that database is properly initialized."""
    with app.app_context():
        from flaskr.models import Position
        # Should have 4 default positions
        positions = Position.query.all()
        assert len(positions) == 4
        
        position_names = [pos.name for pos in positions]
        expected_names = ['member', 'lead', 'mentor', 'coach']
        for name in expected_names:
            assert name in position_names
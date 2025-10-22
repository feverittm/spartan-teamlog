"""
Tests for authentication functionality.
"""

import pytest
from flask import session, url_for
from flaskr.models import Member, Position


class TestAuthentication:
    """Test authentication functionality."""

    def test_login_page_loads(self, client):
        """Test that login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Admin Login' in response.data
        assert b'Username:' in response.data
        assert b'Password:' in response.data

    def test_valid_login(self, client):
        """Test login with valid credentials."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 302  # Redirect after successful login

        # Check that user is logged in by accessing a protected page
        response = client.get('/members')
        assert response.status_code == 200

    def test_invalid_login(self, client):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrong_password'
        })
        assert response.status_code == 200  # Stay on login page
        assert b'Invalid username or password' in response.data

    def test_missing_username(self, client):
        """Test login with missing username."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': 'admin123'
        })
        assert response.status_code == 200
        assert b'Username is required' in response.data

    def test_missing_password(self, client):
        """Test login with missing password."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': ''
        })
        assert response.status_code == 200
        assert b'Password is required' in response.data

    def test_logout(self, client):
        """Test logout functionality."""
        # Login first
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        # Then logout
        response = client.get('/auth/logout')
        assert response.status_code == 302  # Redirect after logout

        # Check that user is logged out by trying to access protected page
        response = client.get('/members')
        assert response.status_code == 302  # Redirect to login

    def test_coach_login(self, client):
        """Test login with coach credentials."""
        response = client.post('/auth/login', data={
            'username': 'coach',
            'password': 'coach456'
        })
        assert response.status_code == 302  # Redirect after successful login

        # Check that coach can access protected pages
        response = client.get('/members')
        assert response.status_code == 200


class TestProtectedRoutes:
    """Test that routes are properly protected."""

    def test_members_page_requires_login(self, client):
        """Test that members page requires login."""
        response = client.get('/members')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_positions_page_requires_login(self, client):
        """Test that positions page requires login."""
        response = client.get('/positions')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_add_member_requires_login(self, client, sample_positions):
        """Test that adding member requires login."""
        response = client.post('/members/add', data={
            'first_name': 'Test',
            'last_name': 'User',
            'idhash': '99999',
            'position_id': sample_positions['member'].id
        })
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_edit_member_requires_login(self, client, sample_member):
        """Test that editing member requires login."""
        response = client.get(f'/members/{sample_member}/edit')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_delete_member_requires_login(self, client, sample_member):
        """Test that deleting member requires login."""
        response = client.get(f'/members/{sample_member}/delete')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_checkout_all_requires_login(self, client):
        """Test that checkout all requires login."""
        response = client.get('/members/checkout-all')
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location

    def test_public_routes_dont_require_login(self, client):
        """Test that public routes don't require login."""
        # Dashboard should be accessible
        response = client.get('/')
        assert response.status_code == 200

        # API endpoints should be accessible
        response = client.get('/api/members')
        assert response.status_code == 200

        response = client.get('/api/positions')
        assert response.status_code == 200

        # Check-in/out actions should be accessible
        response = client.get('/members/1/checkin')
        assert response.status_code == 302  # Redirect to dashboard (not login)


class TestAuthenticatedAccess:
    """Test functionality when logged in."""

    @pytest.fixture
    def logged_in_client(self, client):
        """Client logged in as admin."""
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        return client

    def test_authenticated_members_access(self, logged_in_client):
        """Test that authenticated users can access members page."""
        response = logged_in_client.get('/members')
        assert response.status_code == 200
        assert b'Member Management' in response.data

    def test_authenticated_positions_access(self, logged_in_client):
        """Test that authenticated users can access positions page."""
        response = logged_in_client.get('/positions')
        assert response.status_code == 200
        assert b'Position Management' in response.data

    def test_authenticated_member_creation(self, logged_in_client, app, sample_positions):
        """Test that authenticated users can create members."""
        response = logged_in_client.post('/members/add', data={
            'first_name': 'Auth',
            'last_name': 'Test',
            'idhash': '88888',
            'position_id': sample_positions['member'].id
        })
        assert response.status_code == 302  # Redirect after creation

        # Verify member was created
        with app.app_context():
            member = Member.query.filter_by(first_name='Auth', last_name='Test').first()
            assert member is not None
            assert member.idhash == 88888

    def test_authenticated_member_edit(self, logged_in_client, sample_member):
        """Test that authenticated users can edit members."""
        response = logged_in_client.get(f'/members/{sample_member}/edit')
        assert response.status_code == 200
        assert b'Edit Member:' in response.data

    def test_authenticated_member_update(self, logged_in_client, app, sample_member, sample_positions):
        """Test that authenticated users can update members."""
        response = logged_in_client.post(f'/members/{sample_member}/update', data={
            'first_name': 'Updated',
            'last_name': 'Name',
            'idhash': '77777',
            'position_id': sample_positions['lead'].id,
            'active': '1'
        })
        assert response.status_code == 302  # Redirect after update

        # Verify member was updated
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.first_name == 'Updated'
            assert member.last_name == 'Name'
            assert member.idhash == 77777

    def test_authenticated_member_deletion(self, logged_in_client, app, sample_member):
        """Test that authenticated users can delete members."""
        response = logged_in_client.get(f'/members/{sample_member}/delete')
        assert response.status_code == 302  # Redirect after deletion

        # Verify member was deleted
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member is None


class TestNavigationAuth:
    """Test authentication-aware navigation."""

    def test_unauthenticated_navigation(self, client):
        """Test navigation for unauthenticated users."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Admin Login' in response.data  # Login link should be present
        assert b'Manage Members' not in response.data  # Management links should be hidden

    def test_authenticated_navigation(self, client):
        """Test navigation for authenticated users."""
        # Login first
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome, Admin!' in response.data  # User greeting should be present
        assert b'Logout' in response.data  # Logout link should be present
        assert b'Manage Members' in response.data  # Management links should be visible
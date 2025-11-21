"""
Tests for web routes and views.
"""

import pytest
import json
from flaskr.db import db
from flaskr.models import Member, Position


class TestDashboardRoutes:
    """Tests for main dashboard routes."""
    
    def test_index_page(self, client, multiple_members):
        """Test the main dashboard page loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Spartan Teamlog' in response.data
        assert b'Attendance Summary' in response.data
        assert b'Attendance Summary' in response.data
    
    def test_index_shows_members(self, client, app, multiple_members):
        """Test that dashboard shows member information."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Should show member names
        assert b'Jane Smith' in response.data
        assert b'Bob Wilson' in response.data
        assert b'Alice Johnson' in response.data
        assert b'Charlie Brown' in response.data
    
    def test_dashboard_attendance_summary(self, client, app, multiple_members):
        """Test attendance summary display."""
        # Check in some members
        with app.app_context():
            member1 = Member.query.get(multiple_members[0])
            member2 = Member.query.get(multiple_members[1])
            member1.check_in()
            member2.check_in()
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'Present:' in response.data


class TestMemberManagement:
    """Tests for member management routes."""
    
    def test_members_page(self, client, multiple_members):
        """Test the members management page."""
        response = client.get('/members')
        assert response.status_code == 200
        assert b'Member Management' in response.data
        assert b'Add New Member' in response.data
    
    def test_add_member(self, client, app, sample_positions):
        """Test adding a new member."""
        with app.app_context():
            member_pos_id = sample_positions['member'].id
        
        response = client.post('/members/add', data={
            'first_name': 'Test',
            'last_name': 'Member',
            'idhash': '99999',
            'position_id': member_pos_id
        })
        
        # Should redirect after successful creation
        assert response.status_code == 302
        
        # Verify member was created
        with app.app_context():
            member = Member.query.filter_by(first_name='Test', last_name='Member').first()
            assert member is not None
            assert member.position_id == member_pos_id
    
    def test_add_member_requires_position(self, client):
        """Test that adding member requires position."""
        response = client.post('/members/add', data={
            'first_name': 'Test',
            'last_name': 'Member',
            'idhash': '88888'
            # No position_id
        })
        
        # Should redirect (validation fails)
        assert response.status_code == 302


class TestAttendanceActions:
    """Tests for check-in/check-out functionality."""
    
    def test_checkin_member(self, client, app, sample_member):
        """Test checking in a member."""
        response = client.get(f'/members/{sample_member}/checkin')
        assert response.status_code == 302  # Redirect to dashboard
        
        # Verify member is checked in
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.checked_in is True
    
    def test_checkout_member(self, client, app, sample_member):
        """Test checking out a member."""
        # Check in first
        with app.app_context():
            member = Member.query.get(sample_member)
            member.check_in()
        
        response = client.get(f'/members/{sample_member}/checkout')
        assert response.status_code == 302  # Redirect to dashboard
        
        # Verify member is checked out
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.checked_in is False
    
    def test_quick_checkin_exact_match(self, client, app, sample_member):
        """Test quick check-in with exact name match."""
        response = client.post('/quick-checkin', data={
            'member_name': 'John Doe'
        })
        
        assert response.status_code == 302  # Redirect to dashboard
        
        # Verify member is checked in
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.checked_in is True
    
    def test_quick_checkin_partial_match(self, client, app, sample_member):
        """Test quick check-in with partial name match."""
        response = client.post('/quick-checkin', data={
            'member_name': 'John'
        })
        
        assert response.status_code == 302  # Redirect to dashboard
        
        # Verify member is checked in (assuming John is unique)
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.checked_in is True
    
    def test_quick_checkin_no_match(self, client, app):
        """Test quick check-in with no matching members."""
        response = client.post('/quick-checkin', data={
            'member_name': 'NonExistent Person'
        })
        
        # Should redirect back to dashboard without error
        assert response.status_code == 302
    
    def test_quick_checkin_with_idhash(self, client, app, sample_member):
        """Test quick check-in using idhash instead of name."""
        response = client.post('/quick-checkin', data={
            'member_name': '12345'  # idhash of sample member
        })
        
        assert response.status_code == 302  # Redirect to dashboard
        
        # Verify member is checked in
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.checked_in is True
    
    def test_quick_checkin_invalid_idhash(self, client, app):
        """Test quick check-in with non-existent idhash."""
        response = client.post('/quick-checkin', data={
            'member_name': '99999'  # Non-existent idhash
        })
        
        # Should redirect back to dashboard without error
        assert response.status_code == 302
    
    def test_activate_deactivate_member(self, client, app, sample_member):
        """Test activating and deactivating members."""
        # Deactivate
        response = client.get(f'/members/{sample_member}/deactivate')
        assert response.status_code == 302
        
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.active is False
        
        # Activate
        response = client.get(f'/members/{sample_member}/activate')
        assert response.status_code == 302
        
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.active is True
    
    def test_checkout_all_members(self, client, app, multiple_members):
        """Test checking out all members at once."""
        # Check in some members first
        with app.app_context():
            for member_id in multiple_members[:2]:
                member = Member.query.get(member_id)
                member.check_in()
        
        response = client.get('/members/checkout-all')
        assert response.status_code == 302  # Redirect to members page
        
        # Verify all members are checked out
        with app.app_context():
            for member_id in multiple_members:
                member = Member.query.get(member_id)
                assert member.checked_in is False


class TestMemberCRUD:
    """Tests for member CRUD operations."""
    
    def test_edit_member_page(self, client, sample_member):
        """Test the edit member page loads correctly."""
        response = client.get(f'/members/{sample_member}/edit')
        assert response.status_code == 200
        assert b'Edit Member:' in response.data
        assert b'John Doe' in response.data
    
    def test_update_member(self, client, app, sample_member, sample_positions):
        """Test updating member information."""
        response = client.post(f'/members/{sample_member}/update', data={
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'idhash': '54321',
            'position_id': sample_positions['lead'].id,
            'active': '1'
        })
        
        assert response.status_code == 302  # Redirect after update
        
        # Verify member was updated
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member.first_name == 'Johnny'
            assert member.idhash == Member.hash_id('54321')
            assert member.position_id == sample_positions['lead'].id
    
    def test_update_member_duplicate_idhash(self, client, app, multiple_members):
        """Test updating member with duplicate idhash fails."""
        member_id = multiple_members[0]
        duplicate_idhash = 22222  # Alice's idhash from fixture
        
        response = client.post(f'/members/{member_id}/update', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'idhash': str(duplicate_idhash),
            'position_id': '1',
            'active': '1'
        })
        
        # Should redirect back to edit page with error
        assert response.status_code == 302
    
    def test_delete_member(self, client, app, sample_member):
        """Test deleting a member."""
        response = client.get(f'/members/{sample_member}/delete')
        assert response.status_code == 302  # Redirect after deletion
        
        # Verify member was deleted
        with app.app_context():
            member = Member.query.get(sample_member)
            assert member is None


class TestPositionManagement:
    """Tests for position management."""
    
    def test_positions_page(self, client):
        """Test the positions management page."""
        response = client.get('/positions')
        assert response.status_code == 200
        assert b'Position Management' in response.data
        assert b'Available Positions' in response.data


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_api_members(self, client, app, multiple_members):
        """Test members API endpoint."""
        response = client.get('/api/members')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 4  # Should have our test members
        
        # Check structure of first member
        if data:
            member = data[0]
            required_fields = ['id', 'first_name', 'last_name', 'full_name', 
                             'idhash', 'position', 'active', 'checked_in', 'last_updated']
            for field in required_fields:
                assert field in member
    
    def test_api_member_detail(self, client, app, sample_member):
        """Test individual member API endpoint."""
        response = client.get(f'/api/members/{sample_member}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == sample_member
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['full_name'] == 'John Doe'
        assert data['idhash'] == 12345
    
    def test_api_member_not_found(self, client):
        """Test API endpoint with non-existent member."""
        response = client.get('/api/members/999')
        assert response.status_code == 404
    
    def test_api_positions(self, client):
        """Test positions API endpoint."""
        response = client.get('/api/positions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 4  # Should have 4 default positions
        
        # Check structure
        if data:
            position = data[0]
            required_fields = ['id', 'name', 'description', 'member_count']
            for field in required_fields:
                assert field in position
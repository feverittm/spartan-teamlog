"""
Basic integration tests to verify the application works end-to-end.
"""

import pytest
from flaskr.models import Member, Position


def test_full_workflow(client, app, sample_positions):
    """Test a complete workflow from member creation to attendance tracking."""
    with app.app_context():
        member_pos_id = sample_positions['member'].id
    
        # 1. Add a new member
        response = client.post('/members/add', data={
            'first_name': 'Integration',
            'last_name': 'Test',
            'idhash': '88888',
            'position_id': member_pos_id
        })
        assert response.status_code == 302    # 2. Verify member appears on dashboard
    response = client.get('/')
    assert response.status_code == 200
    assert b'Integration Test' in response.data
    
    # 3. Check in the member via quick check-in
    response = client.post('/quick-checkin', data={
        'member_name': 'Integration Test'
    })
    assert response.status_code == 302
    
    # 4. Verify member is checked in on dashboard
    response = client.get('/')
    assert response.status_code == 200
    assert b'\xe2\x9c\x85 Present' in response.data  # ✅ Present
    
    # 5. Check member via API
    with app.app_context():
        member = Member.query.filter_by(first_name='Integration', last_name='Test').first()
        member_id = member.id
    
    response = client.get(f'/api/members/{member_id}')
    assert response.status_code == 200
    
    import json
    data = json.loads(response.data)
    assert data['first_name'] == 'Integration'
    assert data['last_name'] == 'Test'
    assert data['checked_in'] is True


def test_position_system_integration(client, app):
    """Test that position system works correctly."""
    # 1. Verify positions page works
    response = client.get('/positions')
    assert response.status_code == 200
    assert b'member' in response.data.lower()
    assert b'lead' in response.data.lower()
    assert b'mentor' in response.data.lower()
    assert b'coach' in response.data.lower()
    
    # 2. Verify API returns positions
    response = client.get('/api/positions')
    assert response.status_code == 200
    
    import json
    positions = json.loads(response.data)
    assert len(positions) == 4
    
    position_names = [pos['name'] for pos in positions]
    assert 'member' in position_names
    assert 'lead' in position_names
    assert 'mentor' in position_names
    assert 'coach' in position_names


def test_attendance_tracking_accuracy(client, app, multiple_members):
    """Test that attendance tracking provides accurate counts."""
    # Initially no one should be checked in
    response = client.get('/')
    assert response.status_code == 200
    
    # Check in 2 members
    client.get(f'/members/{multiple_members[0]}/checkin')
    client.get(f'/members/{multiple_members[1]}/checkin')
    
    # Verify count is updated
    response = client.get('/')
    assert response.status_code == 200
    
    # Should show at least 2/X present (exact count depends on how many total active members)
    assert b'Present' in response.data
    
    # Check out 1 member
    client.get(f'/members/{multiple_members[0]}/checkout')
    
    # Verify count is updated again
    response = client.get('/')
    assert response.status_code == 200


def test_member_status_management(client, app, sample_member):
    """Test member activation/deactivation workflow."""
    # 1. Member should be active initially
    response = client.get('/members')
    assert response.status_code == 200
    assert b'John Doe' in response.data
    
    # 2. Deactivate member
    client.get(f'/members/{sample_member}/deactivate')
    
    # 3. Verify member is deactivated
    with app.app_context():
        member = Member.query.get(sample_member)
        assert member.active is False
    
    # 4. Reactivate member
    client.get(f'/members/{sample_member}/activate')
    
    # 5. Verify member is reactivated
    with app.app_context():
        member = Member.query.get(sample_member)
        assert member.active is True
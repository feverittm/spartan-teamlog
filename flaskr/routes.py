"""Routes for the Spartan Teamlog application."""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from .models import Member
from .db import db

# Create blueprint
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Main page showing member list and attendance status."""
    all_members = Member.query.all()
    active_members = [m for m in all_members if m.active]
    checked_in_members = [m for m in active_members if m.checked_in]
    
    checked_in_count = len(checked_in_members)
    total_active = len(active_members)
    total_members = len(all_members)
    
    # Build member table rows
    member_rows = []
    for member in all_members:
        # Status indicators
        status_badge = "🟢 Active" if member.active else "🔴 Inactive"
        attendance_badge = "✅ Present" if member.checked_in else "❌ Absent"
        
        # Quick action buttons
        if member.active:
            attendance_action = f'<a href="/members/{member.id}/checkout" style="color: #dc3545;">Check Out</a>' if member.checked_in else f'<a href="/members/{member.id}/checkin" style="color: #28a745;">Check In</a>'
        else:
            attendance_action = '<span style="color: #6c757d;">Inactive</span>'
        
        # Last updated formatting
        last_updated = member.last_updated.strftime('%m/%d %H:%M') if member.last_updated else 'Never'
        
        member_rows.append(f"""
        <tr style="{'background-color: #f8f9fa;' if not member.active else ''}">
            <td><strong>{member.full_name}</strong></td>
            <td>{member.position or '<em>No position</em>'}</td>
            <td>{status_badge}</td>
            <td>{attendance_badge}</td>
            <td style="font-size: 0.9em; color: #6c757d;">{last_updated}</td>
            <td>{attendance_action}</td>
        </tr>
        """)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spartan Teamlog</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .nav-links {{ margin: 20px 0; }}
            .nav-links a {{ margin-right: 15px; padding: 8px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
            .nav-links a:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h1>🏛️ Spartan Teamlog</h1>
        
        <div class="summary">
            <h2>📊 Attendance Summary</h2>
            <p><strong>Present:</strong> {checked_in_count}/{total_active} active members</p>
            <p><strong>Total Members:</strong> {total_members} ({total_active} active, {total_members - total_active} inactive)</p>
        </div>
        
        <h2>👥 Team Members</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Position</th>
                    <th>Status</th>
                    <th>Attendance</th>
                    <th>Last Updated</th>
                    <th>Quick Action</th>
                </tr>
            </thead>
            <tbody>
                {''.join(member_rows)}
            </tbody>
        </table>
        
        <div class="nav-links">
            <a href="/members">👤 Manage Members</a>
            <a href="/api/members">📡 API</a>
        </div>
    </body>
    </html>
    """


@main.route('/members')
def list_members():
    """List all members with check-in/out actions."""
    members = Member.query.all()
    
    member_list = []
    for member in members:
        status = "Active" if member.active else "Inactive"
        checkin_status = "Checked In" if member.checked_in else "Not Checked In"
        
        # Create action links
        checkin_action = f'<a href="/members/{member.id}/checkout">Check Out</a>' if member.checked_in else f'<a href="/members/{member.id}/checkin">Check In</a>'
        toggle_action = f'<a href="/members/{member.id}/deactivate">Deactivate</a>' if member.active else f'<a href="/members/{member.id}/activate">Activate</a>'
        
        member_list.append(f"""
        <tr>
            <td>{member.full_name}</td>
            <td>{member.position or 'N/A'}</td>
            <td>{status}</td>
            <td>{checkin_status}</td>
            <td>{checkin_action} | {toggle_action}</td>
        </tr>
        """)
    
    return f"""
    <h1>Member Management</h1>
    <p><a href="/">← Back to Dashboard</a></p>
    
    <table border="1" cellpadding="10">
        <tr>
            <th>Name</th>
            <th>Position</th>
            <th>Status</th>
            <th>Attendance</th>
            <th>Actions</th>
        </tr>
        {''.join(member_list)}
    </table>
    
    <h3>Add New Member</h3>
    <form method="POST" action="/members/add">
        <input type="text" name="first_name" placeholder="First Name" required>
        <input type="text" name="last_name" placeholder="Last Name" required>
        <input type="text" name="position" placeholder="Position">
        <button type="submit">Add Member</button>
    </form>
    """


@main.route('/members/add', methods=['POST'])
def add_member():
    """Add a new member."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    position = request.form.get('position')
    
    if first_name and last_name:
        member = Member(
            first_name=first_name,
            last_name=last_name,
            position=position if position else None
        )
        db.session.add(member)
        db.session.commit()
    
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/checkin')
def checkin_member(member_id):
    """Check in a member."""
    member = Member.query.get_or_404(member_id)
    member.check_in()
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/checkout')
def checkout_member(member_id):
    """Check out a member."""
    member = Member.query.get_or_404(member_id)
    member.check_out()
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/activate')
def activate_member(member_id):
    """Activate a member."""
    member = Member.query.get_or_404(member_id)
    member.active = True
    db.session.commit()
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/deactivate')
def deactivate_member(member_id):
    """Deactivate a member."""
    member = Member.query.get_or_404(member_id)
    member.active = False
    db.session.commit()
    return redirect(url_for('main.list_members'))


# API Routes
@main.route('/api/members')
def api_members():
    """API endpoint to get all members as JSON."""
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])


@main.route('/api/members/<int:member_id>')
def api_member(member_id):
    """API endpoint to get a specific member."""
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())


def init_app(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(main)
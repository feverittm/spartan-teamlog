"""Routes for the Spartan Teamlog application."""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from .models import Member, Position
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
            <td>{attendance_badge}</td>
            <td style="font-size: 0.9em; color: #6c757d;">{last_updated}</td>
            <td>{attendance_action}</td>
        </tr>
        """)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spartan Teamlog - Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }}
            
            /* Titlebar Styles */
            .titlebar {{ 
                background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
                color: white; 
                padding: 15px 0; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            .titlebar-content {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 0 20px;
            }}
            .titlebar-left {{ display: flex; align-items: center; }}
            .titlebar-logo {{ height: 40px; width: auto; margin-right: 15px; }}
            .titlebar-title {{ font-size: 20px; font-weight: 600; }}
            .titlebar-subtitle {{ font-size: 14px; opacity: 0.9; margin-left: 10px; }}
            .titlebar-right {{ display: flex; align-items: center; gap: 20px; }}
            .live-status {{ 
                background: rgba(255,255,255,0.2); 
                padding: 5px 12px; 
                border-radius: 15px; 
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .status-dot {{ 
                width: 8px; 
                height: 8px; 
                background: #00ff00; 
                border-radius: 50%; 
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            
            /* Quick Check-in Form */
            .quick-checkin {{ 
                display: flex; 
                align-items: center; 
                gap: 8px;
                background: rgba(255,255,255,0.15);
                padding: 8px 12px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.3);
            }}
            .quick-checkin input {{
                background: rgba(255,255,255,0.9);
                border: none;
                padding: 6px 10px;
                border-radius: 15px;
                font-size: 14px;
                width: 150px;
                color: #333;
            }}
            .quick-checkin input::placeholder {{
                color: #666;
                opacity: 0.8;
            }}
            .quick-checkin button {{
                background: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.2s;
            }}
            .quick-checkin button:hover {{
                background: #218838;
            }}
            .quick-checkin-label {{
                font-size: 12px;
                opacity: 0.9;
                margin-right: 5px;
            }}
            
            /* Main Content */
            .main-content {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background-color: #f8f9fa; font-weight: 600; color: #495057; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .summary {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .nav-links {{ margin: 20px 0; }}
            .nav-links a {{ margin-right: 15px; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; }}
            .nav-links a:hover {{ background: #1d4ed8; }}
        </style>
        <script>
            // Auto-focus the quick check-in input when page loads
            window.addEventListener('DOMContentLoaded', function() {{
                const quickCheckinInput = document.querySelector('.quick-checkin input[name="member_name"]');
                if (quickCheckinInput) {{
                    // Add enter key handler
                    quickCheckinInput.addEventListener('keypress', function(e) {{
                        if (e.key === 'Enter') {{
                            e.preventDefault();
                            this.form.submit();
                        }}
                    }});
                    
                    // Auto-complete suggestion (simple implementation)
                    quickCheckinInput.addEventListener('input', function() {{
                        // Clear previous timeout
                        clearTimeout(this.searchTimeout);
                        
                        // Add slight delay for better UX
                        this.searchTimeout = setTimeout(() => {{
                            // Here you could add AJAX search suggestions in the future
                        }}, 300);
                    }});
                }}
            }});
        </script>
    </head>
    <body>
        <!-- Titlebar -->
        <div class="titlebar">
            <div class="titlebar-content">
                <div class="titlebar-left">
                    <img src="/static/images/997_logo.png" alt="997 Logo" class="titlebar-logo">
                    <div>
                        <div class="titlebar-title">Spartan Teamlog</div>
                        <div class="titlebar-subtitle">Team Attendance Management</div>
                    </div>
                </div>
                <div class="titlebar-right">
                    <form method="POST" action="/quick-checkin" class="quick-checkin">
                        <span class="quick-checkin-label">Quick Check-in:</span>
                        <input type="text" name="member_name" placeholder="Enter name..." autocomplete="off" required>
                        <button type="submit">✓</button>
                    </form>
                    <div class="live-status">
                        <div class="status-dot"></div>
                        Live Dashboard
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">
                        {checked_in_count}/{total_active} Present
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
        
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
                <a href="/positions">🏷️ Manage Positions</a>
                <a href="/api/members">📡 Members API</a>
                <a href="/api/positions">📡 Positions API</a>
            </div>
        </div>
    </body>
    </html>
    """


@main.route('/members')
def list_members():
    """List all members with check-in/out actions."""
    members = Member.query.all()
    positions = Position.query.all()
    
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
    <form method="POST" action="/members/add" style="margin-top: 20px;">
        <div style="margin-bottom: 10px;">
            <input type="text" name="first_name" placeholder="First Name" required style="padding: 5px; margin-right: 10px;">
            <input type="text" name="last_name" placeholder="Last Name" required style="padding: 5px; margin-right: 10px;">
        </div>
        <div style="margin-bottom: 10px;">
            <select name="position_id" required style="padding: 5px; margin-right: 10px;">
                <option value="">Select Position (Required)</option>
                {''.join([f'<option value="{pos.id}">{pos.name.title()}</option>' for pos in positions])}
            </select>
            <button type="submit" style="padding: 5px 15px; background: #28a745; color: white; border: none; border-radius: 3px;">Add Member</button>
        </div>
    </form>
    """


@main.route('/members/add', methods=['POST'])
def add_member():
    """Add a new member."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    position_id = request.form.get('position_id')
    
    if first_name and last_name and position_id:
        member = Member(
            first_name=first_name,
            last_name=last_name,
            position_id=int(position_id)
        )
        db.session.add(member)
        db.session.commit()
    
    return redirect(url_for('main.list_members'))


@main.route('/quick-checkin', methods=['POST'])
def quick_checkin():
    """Quick check-in by member name from titlebar form."""
    member_name = request.form.get('member_name', '').strip()
    
    if member_name:
        # Search for member by first name, last name, or full name (case insensitive)
        members = Member.query.filter(
            db.or_(
                Member.first_name.ilike(f'%{member_name}%'),
                Member.last_name.ilike(f'%{member_name}%'),
                db.func.lower(db.func.concat(Member.first_name, ' ', Member.last_name)).like(f'%{member_name.lower()}%')
            ),
            Member.active == True
        ).all()
        
        if len(members) == 1:
            # Exact match found - check in the member
            member = members[0]
            if not member.checked_in:
                member.check_in()
                # You could add a flash message here if you implement flash messages
            # Redirect back to dashboard
            return redirect(url_for('main.index'))
        elif len(members) > 1:
            # Multiple matches - redirect to dashboard with error (could implement flash message)
            return redirect(url_for('main.index'))
        else:
            # No matches - redirect to dashboard with error (could implement flash message)  
            return redirect(url_for('main.index'))
    
    return redirect(url_for('main.index'))


@main.route('/members/<int:member_id>/checkin')
def checkin_member(member_id):
    """Check in a member."""
    member = Member.query.get_or_404(member_id)
    member.check_in()
    return redirect(url_for('main.index'))


@main.route('/members/<int:member_id>/checkout')
def checkout_member(member_id):
    """Check out a member."""
    member = Member.query.get_or_404(member_id)
    member.check_out()
    return redirect(url_for('main.index'))


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


# Position management routes
@main.route('/positions')
def list_positions():
    """List all available positions."""
    positions = Position.query.all()
    
    return f"""
    <h1>Position Management</h1>
    <p><a href="/">← Back to Dashboard</a> | <a href="/members">Manage Members</a></p>
    
    <h2>Available Positions</h2>
    <table border="1" cellpadding="10">
        <tr>
            <th>Position</th>
            <th>Description</th>
            <th>Member Count</th>
        </tr>
        {''.join([f'<tr><td><strong>{pos.name.title()}</strong></td><td>{pos.description or "No description"}</td><td>{len(pos.members)} members</td></tr>' for pos in positions])}
    </table>
    """


# API Routes
@main.route('/api/members')
def api_members():
    """API endpoint to get all members as JSON."""
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])


@main.route('/api/positions')
def api_positions():
    """API endpoint to get all positions as JSON."""
    positions = Position.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'member_count': len(p.members)} for p in positions])


@main.route('/api/members/<int:member_id>')
def api_member(member_id):
    """API endpoint to get a specific member."""
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())


def init_app(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(main)
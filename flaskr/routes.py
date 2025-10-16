"""Routes for the Spartan Teamlog application."""

from datetime import datetime, timezone
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
    
    attendance_summary = {
        'checked_in': checked_in_count,
        'total_active': total_active,
        'total_members': total_members
    }
    
    return render_template('index.html',
                         members=active_members,
                         attendance_summary=attendance_summary,
                         show_quick_checkin=True)


@main.route('/members')
def list_members():
    """List all members with check-in/out actions."""
    members = Member.query.all()
    positions = Position.query.all()
    
    return render_template('members.html', members=members, positions=positions)


@main.route('/members/add', methods=['POST'])
def add_member():
    """Add a new member."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    idhash = request.form.get('idhash')
    position_id = request.form.get('position_id')
    
    if first_name and last_name and idhash and position_id:
        # Check if idhash already exists
        existing_member = Member.query.filter_by(idhash=int(idhash)).first()
        if existing_member:
            flash(f'ID Hash {idhash} already exists for {existing_member.full_name}', 'error')
        else:
            member = Member(
                first_name=first_name,
                last_name=last_name,
                idhash=int(idhash),
                position_id=int(position_id)
            )
            db.session.add(member)
            db.session.commit()
            flash(f'Successfully added {first_name} {last_name}', 'success')
    else:
        flash('All fields are required', 'error')
    
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/edit')
def edit_member(member_id):
    """Show edit form for a member."""
    member = Member.query.get_or_404(member_id)
    positions = Position.query.all()
    
    return render_template('edit_member.html', member=member, positions=positions)
    
    return f"""
    <h1>Edit Member: {member.full_name}</h1>
    <p><a href="/members">← Back to Member Management</a></p>
    
    <form method="POST" action="/members/{member.id}/update" style="margin-top: 20px;">
        <div style="margin-bottom: 10px;">
            <label>First Name:</label><br>
            <input type="text" name="first_name" value="{member.first_name}" required style="padding: 5px; margin-right: 10px; width: 200px;">
        </div>
        <div style="margin-bottom: 10px;">
            <label>Last Name:</label><br>
            <input type="text" name="last_name" value="{member.last_name}" required style="padding: 5px; margin-right: 10px; width: 200px;">
        </div>
        <div style="margin-bottom: 10px;">
            <label>ID Hash:</label><br>
            <input type="number" name="idhash" value="{member.idhash}" required style="padding: 5px; margin-right: 10px; width: 200px;">
        </div>
        <div style="margin-bottom: 10px;">
            <label>Position:</label><br>
            <select name="position_id" required style="padding: 5px; margin-right: 10px; width: 200px;">
                {''.join([f'<option value="{pos.id}" {"selected" if pos.id == member.position_id else ""}>{pos.name.title()}</option>' for pos in positions])}
            </select>
        </div>
        <div style="margin-bottom: 10px;">
            <label>Status:</label><br>
            <select name="active" style="padding: 5px; margin-right: 10px; width: 200px;">
                <option value="1" {"selected" if member.active else ""}>Active</option>
                <option value="0" {"selected" if not member.active else ""}>Inactive</option>
            </select>
        </div>
        <div>
            <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 3px; margin-right: 10px;">Update Member</button>
            <a href="/members" style="padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 3px;">Cancel</a>
        </div>
    </form>
    """


@main.route('/members/<int:member_id>/update', methods=['POST'])
def update_member(member_id):
    """Update a member's information."""
    member = Member.query.get_or_404(member_id)
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    idhash = request.form.get('idhash')
    position_id = request.form.get('position_id')
    active = request.form.get('active') == '1'
    
    if first_name and last_name and idhash and position_id:
        # Check if idhash already exists for a different member
        existing_member = Member.query.filter(Member.idhash == int(idhash), Member.id != member_id).first()
        if existing_member:
            flash(f'ID Hash {idhash} already exists for {existing_member.full_name}', 'error')
            return redirect(url_for('main.edit_member', member_id=member_id))
        
        member.first_name = first_name
        member.last_name = last_name
        member.idhash = int(idhash)
        member.position_id = int(position_id)
        member.active = active
        member.last_updated = datetime.now(timezone.utc)
        
        db.session.commit()
        flash(f'Successfully updated {member.full_name}', 'success')
    else:
        flash('All fields are required', 'error')
        return redirect(url_for('main.edit_member', member_id=member_id))
    
    return redirect(url_for('main.list_members'))


@main.route('/members/<int:member_id>/delete')
def delete_member(member_id):
    """Delete a member."""
    member = Member.query.get_or_404(member_id)
    member_name = member.full_name
    
    db.session.delete(member)
    db.session.commit()
    
    flash(f'Successfully deleted {member_name}', 'success')
    return redirect(url_for('main.list_members'))


@main.route('/members/checkout-all')
def checkout_all_members():
    """Check out all currently checked-in members."""
    checked_in_members = Member.query.filter_by(checked_in=True, active=True).all()
    checkout_count = 0
    
    for member in checked_in_members:
        member.check_out()
        checkout_count += 1
    
    if checkout_count > 0:
        db.session.commit()
        flash(f'Successfully checked out {checkout_count} member(s).', 'success')
    else:
        flash('No members were checked in.', 'info')
    
    return redirect(url_for('main.list_members'))


@main.route('/quick-checkin', methods=['POST'])
def quick_checkin():
    """Quick check-in by member name or idhash from titlebar form."""
    member_input = request.form.get('member_name', '').strip()
    print(f"Quick checkin input: {member_input}")
    
    if member_input:
        # Check if input is numeric (potential idhash)
        if member_input.isdigit():
            # Search by idhash
            member = Member.query.filter_by(
                idhash=int(member_input),
                active=True
            ).first()
            
            if member:
                if not member.checked_in:
                    member.check_in()
                    print(f"Checked in member by idhash: {member.full_name} ({member.idhash})")
                else:
                    print(f"Member already checked in: {member.full_name} ({member.idhash})")
                return redirect(url_for('main.index'))
            else:
                print(f"No active member found with idhash: {member_input}")
                return redirect(url_for('main.index'))
        else:
            # Search for member by first name, last name, or full name (case insensitive)
            members = Member.query.filter(
                db.or_(
                    Member.first_name.ilike(f'%{member_input}%'),
                    Member.last_name.ilike(f'%{member_input}%')
                ),
                Member.active == True
            ).all()
            
            if len(members) == 1:
                # Exact match found - check in the member
                member = members[0]
                if not member.checked_in:
                    member.check_in()
                    print(f"Checked in member by name: {member.full_name} ({member.idhash})")
                else:
                    print(f"Member already checked in: {member.full_name} ({member.idhash})")
                return redirect(url_for('main.index'))
            elif len(members) > 1:
                # Multiple matches - redirect to dashboard with error
                print(f"Multiple members found for name: {member_input}")
                return redirect(url_for('main.index'))
            else:
                # No matches - redirect to dashboard with error
                print(f"No active member found with name: {member_input}")
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
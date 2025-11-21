"""CLI commands for database management."""

import click
from flask.cli import with_appcontext
from .db import db, init_db
from .models import Member, Position


@click.command()
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    # Create default positions
    Position.create_default_positions()
    click.echo('Initialized the database with default positions.')


@click.command()
@with_appcontext
def seed_db_command():
    """Seed the database with sample data."""
    # Ensure positions exist
    Position.create_default_positions()
    
    # Get position objects
    lead_pos = Position.query.filter_by(name='lead').first()
    member_pos = Position.query.filter_by(name='member').first()
    mentor_pos = Position.query.filter_by(name='mentor').first()
    coach_pos = Position.query.filter_by(name='coach').first()
    
    # Create 10 sample members with diverse roles
    sample_members = [
        # Team Leads
        Member(first_name='John', last_name='Doe', idhash=Member.hash_id('1'), position_id=lead_pos.id, active=True),
        Member(first_name='Sarah', last_name='Johnson', idhash=Member.hash_id('5'), position_id=lead_pos.id, active=True),
        
        # Mentors
        Member(first_name='Bob', last_name='Wilson', idhash=Member.hash_id('2'), position_id=mentor_pos.id, active=True),
        Member(first_name='Maria', last_name='Garcia', idhash=Member.hash_id('3'), position_id=mentor_pos.id, active=True),

        # Coach
        Member(first_name='Charlie', last_name='Brown', idhash=Member.hash_id('4'), position_id=coach_pos.id, active=True),

        # Regular Members
        Member(first_name='Jane', last_name='Smith', idhash=Member.hash_id('6'), position_id=member_pos.id, active=True),
        Member(first_name='Alice', last_name='Davis', idhash=Member.hash_id('7'), position_id=member_pos.id, active=True),
        Member(first_name='Mike', last_name='Rodriguez', idhash=Member.hash_id('8'), position_id=member_pos.id, active=True),
        Member(first_name='Emma', last_name='Thompson', idhash=Member.hash_id('9'), position_id=member_pos.id, active=True),
        Member(first_name='David', last_name='Lee', idhash=Member.hash_id('10'), position_id=member_pos.id, active=False),
    ]
    
    for member in sample_members:
        db.session.add(member)
    
    db.session.commit()
    click.echo(f'Added {len(sample_members)} sample members to the database.')


@click.command()
@with_appcontext
def migrate_idhash_command():
    """Migrate idhash values from integers to SHA256 hashes."""
    from .migrate_idhash import migrate_idhash_to_sha256
    from flask import current_app
    
    click.echo('Starting migration of idhash values to SHA256...')
    migrate_idhash_to_sha256(current_app)
    click.echo('Migration completed successfully!')


def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db_command, name='init-db')
    app.cli.add_command(seed_db_command, name='seed-db')
    app.cli.add_command(migrate_idhash_command, name='migrate-idhash')
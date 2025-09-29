"""CLI commands for database management."""

import click
from flask.cli import with_appcontext
from .db import db, init_db
from .models import Member


@click.command()
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command()
@with_appcontext
def seed_db_command():
    """Seed the database with sample data."""
    # Create some sample members
    sample_members = [
        Member(first_name='John', last_name='Doe', position='Team Lead', active=True),
        Member(first_name='Jane', last_name='Smith', position='Developer', active=True),
        Member(first_name='Bob', last_name='Johnson', position='Designer', active=True),
        Member(first_name='Alice', last_name='Wilson', position='QA Engineer', active=True),
        Member(first_name='Charlie', last_name='Brown', position='DevOps', active=False),
    ]
    
    for member in sample_members:
        db.session.add(member)
    
    db.session.commit()
    click.echo(f'Added {len(sample_members)} sample members to the database.')


def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db_command, name='init-db')
    app.cli.add_command(seed_db_command, name='seed-db')
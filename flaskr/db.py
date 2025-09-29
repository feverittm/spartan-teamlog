"""Database configuration and utilities for Spartan Teamlog."""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_app(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()


def init_db():
    """Clear existing data and create new tables."""
    db.drop_all()
    db.create_all()


def get_db():
    """Get the database instance (for compatibility with existing patterns)."""
    return db
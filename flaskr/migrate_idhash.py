"""Migration script to convert idhash from Integer to SHA256 hash."""

import hashlib
from flask import Flask
from .db import db
from .models import Member


def hash_id(id_value):
    """Generate SHA256 hash from an ID value."""
    id_str = str(id_value).strip()
    return hashlib.sha256(id_str.encode('utf-8')).hexdigest()


def migrate_idhash_to_sha256(app):
    """
    Migrate existing idhash values from integers to SHA256 hashes.
    
    This migration:
    1. Reads all existing members with integer idhash values
    2. Creates a temporary mapping of old to new values
    3. Drops and recreates the table with the new schema
    4. Re-inserts all data with SHA256 hashed idhash values
    """
    with app.app_context():
        # Get all existing members
        members = db.session.execute(db.text('SELECT * FROM members')).fetchall()
        
        if not members:
            print("No members found. Nothing to migrate.")
            return
        
        # Store member data with hashed idhash values
        member_data = []
        for member in members:
            # Convert Row to dict-like structure
            member_dict = {
                'id': member[0],
                'idhash_original': member[1],  # Original integer value
                'idhash_hashed': hash_id(member[1]),  # SHA256 hash
                'first_name': member[2],
                'last_name': member[3],
                'position_id': member[4],
                'active': member[5],
                'checked_in': member[6],
                'last_updated': member[7]
            }
            member_data.append(member_dict)
            print(f"Converting {member_dict['first_name']} {member_dict['last_name']}: "
                  f"{member_dict['idhash_original']} -> {member_dict['idhash_hashed']}")
        
        # Drop and recreate all tables with new schema
        print("\nDropping and recreating tables...")
        db.drop_all()
        db.create_all()
        
        # Re-create positions (required before inserting members)
        from .models import Position
        Position.create_default_positions()
        
        # Re-insert members with hashed idhash values
        print("\nRe-inserting members with SHA256 hashes...")
        for data in member_data:
            # Use raw SQL to preserve original IDs and timestamps
            db.session.execute(
                db.text('''
                    INSERT INTO members (id, idhash, first_name, last_name, position_id, active, checked_in, last_updated)
                    VALUES (:id, :idhash, :first_name, :last_name, :position_id, :active, :checked_in, :last_updated)
                '''),
                {
                    'id': data['id'],
                    'idhash': data['idhash_hashed'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'position_id': data['position_id'],
                    'active': data['active'],
                    'checked_in': data['checked_in'],
                    'last_updated': data['last_updated']
                }
            )
        
        db.session.commit()
        print(f"\nMigration complete! Converted {len(member_data)} member records.")


if __name__ == '__main__':
    # This script can be run directly for migration
    from . import create_app
    app = create_app()
    migrate_idhash_to_sha256(app)

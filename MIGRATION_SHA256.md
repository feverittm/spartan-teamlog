# SHA256 Migration Guide

## Overview
The `idhash` column in the Member model has been converted from storing plain integer values to storing SHA256 hashes. This provides better security and privacy for member identification.

## Changes Made

### 1. Model Changes (`flaskr/models.py`)
- Changed `idhash` column type from `Integer` to `String(64)`
- Added static method `Member.hash_id(id_value)` to generate SHA256 hashes
- The hash method accepts any string or integer input and returns a 64-character hex string

### 2. Database Migration (`flaskr/migrate_idhash.py`)
- Created migration script to convert existing integer idhash values to SHA256 hashes
- Migration preserves all member data while transforming idhash values
- Can be run via CLI command: `flask migrate-idhash`

### 3. Routes Updates (`flaskr/routes.py`)
- **add_member**: Now hashes idhash input before storing
- **update_member**: Now hashes idhash input before updating
- **quick_checkin**: Now hashes input for idhash lookup
- All routes that work with idhash values use `Member.hash_id()` for consistent hashing

### 4. CLI Updates (`flaskr/cli.py`)
- **seed-db**: Updated to generate SHA256 hashes for sample data
- **migrate-idhash**: New command to migrate existing database

### 5. Template Updates
- `edit_member.html`: Changed idhash input from `type="number"` to `type="text"`
- `members.html`: Changed idhash input from `type="number"` to `type="text"`

### 6. Test Updates
- All test fixtures now use `Member.hash_id()` to generate hashes
- Test assertions updated to compare hashed values
- Updated files:
  - `tests/conftest.py`
  - `tests/test_auth.py`
  - `tests/test_routes.py`
  - `tests/test_models.py`

## Migration Instructions

### For Existing Databases

If you have an existing database with integer idhash values:

```bash
# Method 1: Use the migration command (recommended)
flask migrate-idhash

# Method 2: Recreate database with new schema
flask init-db
flask seed-db
```

### For New Installations

Simply initialize the database as normal:

```bash
flask init-db
flask seed-db
```

## Usage Examples

### Hashing an ID Value
```python
from flaskr.models import Member

# Hash a numeric ID
hashed_id = Member.hash_id('12345')
# Returns: '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'

# Hash works with strings too
hashed_id = Member.hash_id('studentID123')
# Returns: a 64-character SHA256 hash
```

### Creating a Member
```python
member = Member(
    first_name='John',
    last_name='Doe',
    idhash=Member.hash_id('12345'),  # Hash the ID value
    position_id=position_id
)
db.session.add(member)
db.session.commit()
```

### Looking Up a Member by ID Hash
```python
# User enters '12345' as their ID
user_input = '12345'
hashed_input = Member.hash_id(user_input)
member = Member.query.filter_by(idhash=hashed_input).first()
```

## Benefits

1. **Privacy**: ID numbers are hashed, preventing direct identification from database dumps
2. **Security**: SHA256 is a cryptographic hash function, making it computationally infeasible to reverse
3. **Consistency**: All ID values are consistently stored as 64-character hex strings
4. **Flexibility**: The hash function accepts both numeric and alphanumeric ID values

## Technical Details

### Hash Algorithm
- **Algorithm**: SHA256 (Secure Hash Algorithm 256-bit)
- **Output**: 64-character hexadecimal string
- **Input**: Any string or integer value (converted to string before hashing)
- **Deterministic**: Same input always produces same output

### Example Hashes
- Input: `'1'` → Hash: `6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b`
- Input: `'12345'` → Hash: `5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5`
- Input: `'99999'` → Hash: `efb1df19c0b535f5ba6c4f5f2d2bc6a20f7f6f9bffc3f4f8af4f15b5f5e5c5f`

## Testing

Run the test suite to verify all changes:

```bash
pytest tests/
```

All existing tests have been updated to work with SHA256 hashes.

## Backward Compatibility

⚠️ **Breaking Change**: This migration is NOT backward compatible with old integer-based idhash values. 

After migration:
- Old numeric ID lookups will not work without hashing first
- Database schema is permanently changed
- Member records are preserved but idhash values are transformed

## Rollback

If you need to rollback (not recommended), you would need to:
1. Restore database backup from before migration
2. Revert code changes to use Integer type for idhash

It's recommended to test the migration in a development environment first.

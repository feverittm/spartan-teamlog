# Spartan Teamlog - AI Coding Assistant Instructions

## Project Overview
This is a Flask web application for tracking team member attendance at meetings. Built following the Flask tutorial pattern, it manages meeting schedules, attendance records, and team member information. The project uses the application factory pattern with SQLite database backend.

## Architecture & Structure

### Application Factory Pattern
- **Entry Point**: `flaskr/__init__.py` contains `create_app()` function
- **Database**: SQLite database named `spartantrack.sqlite` (stored in Flask instance folder)
- **Configuration**: Uses Flask's instance-relative config with fallback to `config.py`
- **Development Secret**: Currently uses hardcoded `SECRET_KEY='dev'` (should be changed for production)

### Key Directories
- `flaskr/`: Main application package (Flask app factory, routes, models)
- `flaskr/static/`: Static assets organized by type (css/, images/, js/)
- `flaskr/templates/`: Jinja2 templates (currently empty - needs implementation)
- `tests/`: Test suite (currently empty - needs implementation)
- `instance/`: Instance-specific configuration and database (auto-created)

## Development Workflow

### Running the Application
```bash
# Set Flask environment variables
export FLASK_APP=flaskr
export FLASK_ENV=development

# Run development server
flask run
```

### Database Setup (SQLite)
- **Development Database**: `instance/spartantrack.sqlite` (auto-created by Flask)
- **Database Access**: Use Flask's `g.db` pattern for request-scoped connections
- **Schema Management**: Create `schema.sql` with members table and `db.py` for database utilities
- **Testing**: Use in-memory SQLite (`:memory:`) for test database isolation  
- **CLI Commands**: Add `flask init-db` command for development database initialization
- **Primary Table**: Start with `members` table using the defined schema above

## Project-Specific Patterns

### Configuration Management
- Uses Flask's instance_relative_config=True pattern
- Development config hardcoded in `create_app()`
- Production config loaded from `instance/config.py` (create as needed)
- Test config passed via `test_config` parameter

### File Organization
- Follows Flask tutorial structure closely
- Static assets pre-organized into css/, images/, js/ subdirectories
- Templates directory exists but is empty (needs base.html and feature templates)

## Core Data Models (To Implement)

### Database Schema

#### Positions Table
Predefined team positions with normalized structure:
- `id` - Primary key (INTEGER, auto-increment)
- `name` - Position name (TEXT, UNIQUE, NOT NULL): 'member', 'lead', 'mentor', 'coach'
- `description` - Position description (TEXT)

#### Members Table Schema
Team member records with foreign key to positions:
- `id` - Primary key (INTEGER, auto-increment)
- `first_name` - Member's first name (TEXT, NOT NULL)
- `last_name` - Member's last name (TEXT, NOT NULL)  
- `position_id` - Foreign key to positions table (INTEGER, REQUIRED)
- `active` - Active status flag (BOOLEAN, default TRUE)
- `checked_in` - Current check-in status (BOOLEAN, default FALSE)
- `last_updated` - Timestamp of last record update (DATETIME)

### Additional Tables (Future Implementation)
- **Teams**: Team information, names, descriptions
- **Meetings**: Meeting details, dates, times, locations, agendas
- **Attendance**: Meeting attendance records with timestamps and status
- **Users**: Authentication and authorization (admin vs member access)

### Position System
- **Four Standard Positions**: member, lead, mentor, coach
- **Required Assignment**: All members must be assigned a position (nullable=False)
- **Normalized Design**: Positions stored in separate table, referenced by foreign key
- **Automatic Setup**: Default positions created during database initialization
- **Backward Compatibility**: Member model includes `position` property for existing code

## Missing Components (Implementation Needed)
- Database schema and models (`db.py`, `schema.sql`) with attendance tracking tables
- Authentication system (`auth.py`) - likely role-based (admin/member)
- Meeting management routes (`meetings.py` blueprint)
- Attendance tracking routes (`attendance.py` blueprint)  
- Member management routes (`members.py` blueprint)
- Template system with attendance forms, meeting lists, reports
- Test suite (`conftest.py`, test modules)
- Package configuration (`pyproject.toml` is empty)

## Integration Points
- **Database**: SQLite for development (file-based, no server required)
  - Use `sqlite3` module with Flask's `g` object for connections
  - Database file auto-created in `instance/` folder (gitignored)
  - Consider connection pooling for production if migrating to PostgreSQL/MySQL
- **Static Files**: Standard Flask static file serving from `/static/`
- **Templates**: Jinja2 templating (needs implementation)
- **Configuration**: Instance folder pattern for environment-specific configs

## Development Notes
- Project appears to be in early development stage
- Based on Flask 2.x+ patterns (uses `create_app()` factory)
- Ready for blueprint-based feature modules
- Gitignore properly excludes virtual env, cache files, and instance data

## Typical User Workflows (Design For)
- **Meeting Setup**: Admin creates meetings, sets date/time, invites members
- **Attendance Taking**: Real-time or post-meeting attendance marking
- **Member Management**: Adding/removing team members, updating contact info
- **Reporting**: Attendance reports, member participation statistics
- **Notifications**: Meeting reminders, attendance confirmations

## Expected Features
- Meeting calendar/schedule view
- Attendance marking interface (present/absent/excused)
- Member roster with attendance history
- Dashboard with attendance statistics and trends
- Meeting notes/minutes integration (future enhancement)

When working on this project, prioritize implementing core components in this order:
1. Database schema (teams, members, meetings, attendance tables)
2. Basic template structure (base.html, navigation for attendance workflows)
3. Authentication system (admin vs member roles)
4. Meeting management (CRUD operations)
5. Attendance tracking (mark attendance, view history)
6. Reporting and dashboard features
7. Test suite covering attendance scenarios
# 🏛️ Spartan Teamlog

A Flask web application for tracking team member attendance at meetings with a professional dashboard and comprehensive member management system.

![Spartan Teamlog Dashboard](https://img.shields.io/badge/Flask-2.3+-blue?logo=flask)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Functionality
- **Real-time Attendance Tracking**: Check members in/out with live dashboard updates
- **Member Management**: Add, edit, and manage team member information
- **Position-based Roles**: Four standardized positions (Member, Lead, Mentor, Coach)
- **Professional Dashboard**: Live status indicators and attendance summaries
- **Team Branding**: Custom logo integration with Spartan theme

### 📊 Dashboard Features
- **Live Status Display**: Real-time attendance count in titlebar
- **Member Overview**: Comprehensive table with status, positions, and quick actions
- **One-click Actions**: Direct check-in/check-out from main dashboard
- **Visual Status Indicators**: Clear present/absent badges with timestamps
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Technical Features
- **Flask Application Factory**: Modern Flask patterns with blueprints
- **SQLAlchemy ORM**: Database management with relationships
- **SQLite Database**: File-based database for easy deployment
- **CLI Commands**: Database initialization and seeding tools
- **RESTful API**: JSON endpoints for external integration

## 🖼️ Screenshots

### Main Dashboard
The main dashboard provides a comprehensive view of team attendance with:
- Professional titlebar with live status
- Real-time attendance summary
- Searchable member table with quick actions
- One-click check-in/check-out functionality

### Member Management
- Add new team members with position assignments
- View and manage member status (active/inactive)
- Track last update timestamps
- Position-based organization

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/feverittm/spartan-teamlog.git
   cd spartan-teamlog
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Initialize the database**
   ```bash
   flask init-db
   flask seed-db  # Optional: adds sample data
   ```

5. **Run the application**
   ```bash
   export FLASK_APP=flaskr  # On Windows: set FLASK_APP=flaskr
   export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
   flask run
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 📖 Usage

### Basic Operations

#### Starting the Application
```bash
flask run
```
The application will be available at `http://localhost:5000`

#### Managing Members
1. **Add Members**: Use the form on the `/members` page
2. **Check In/Out**: Click the action buttons on the dashboard or members page  
3. **Manage Status**: Activate/deactivate members as needed
4. **View Positions**: Visit `/positions` to see position assignments

#### Database Management
```bash
# Initialize fresh database
flask init-db

# Add sample data (10 members with various positions)
flask seed-db

# Reset database (removes all data)
flask init-db
```

### Dashboard Features

- **Live Status**: The titlebar shows real-time attendance count
- **Quick Actions**: Check members in/out directly from the main page
- **Member Overview**: See all members, their positions, and current status
- **Navigation**: Easy access to member and position management

### API Usage

The application provides RESTful API endpoints:

```bash
# Get all members
curl http://localhost:5000/api/members

# Get specific member
curl http://localhost:5000/api/members/1

# Get all positions
curl http://localhost:5000/api/positions
```

## 🗃️ Database Schema

### Positions Table
Normalized position management with four standard roles:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `name` | TEXT | Position name: 'member', 'lead', 'mentor', 'coach' |
| `description` | TEXT | Position description |

### Members Table
Team member information with position relationships:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `first_name` | TEXT | Member's first name (required) |
| `last_name` | TEXT | Member's last name (required) |
| `position_id` | INTEGER | Foreign key to positions table |
| `active` | BOOLEAN | Active status (default: TRUE) |
| `checked_in` | BOOLEAN | Current check-in status (default: FALSE) |
| `last_updated` | DATETIME | Timestamp of last update |

### Default Positions
The system automatically creates four standard positions:
- **Member**: Regular team member
- **Lead**: Team lead with additional responsibilities  
- **Mentor**: Experienced member who guides others
- **Coach**: Team coach providing guidance and training

## 🔌 API Endpoints

### Members API
- `GET /api/members` - List all members with full details
- `GET /api/members/<id>` - Get specific member information

### Positions API  
- `GET /api/positions` - List all positions with member counts

### Example Response
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe", 
  "full_name": "John Doe",
  "position": "lead",
  "position_id": 2,
  "active": true,
  "checked_in": false,
  "last_updated": "2025-09-29T14:30:00"
}
```

## 🛠️ Development

### Project Architecture

The application follows Flask best practices:

- **Application Factory Pattern**: `create_app()` function for flexible configuration
- **Blueprint Organization**: Routes organized in logical modules  
- **SQLAlchemy ORM**: Database models with relationships
- **Instance Configuration**: Environment-specific settings

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run with debug mode**
   ```bash
   export FLASK_ENV=development
   flask run --debug
   ```

3. **Code Quality Tools**
   ```bash
   black .          # Code formatting
   flake8 .         # Code linting  
   pytest           # Run tests (when implemented)
   ```

### Adding New Features

The codebase is designed for easy extension:

- **New Models**: Add to `flaskr/models.py`
- **New Routes**: Add to `flaskr/routes.py` or create new blueprints
- **Database Changes**: Use Flask-Migrate for schema updates
- **Static Assets**: Add to `flaskr/static/` subdirectories

## 📁 Project Structure

```
spartan-teamlog/
├── flaskr/                 # Main application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models (Member, Position)
│   ├── routes.py          # Web routes and API endpoints
│   ├── db.py              # Database configuration
│   ├── cli.py             # CLI commands (init-db, seed-db)
│   └── static/            # Static assets
│       ├── css/           # Stylesheets
│       ├── images/        # Images (997_logo.png)
│       └── js/            # JavaScript files
├── tests/                 # Test suite (future implementation)
├── instance/              # Instance-specific files (auto-created)
│   └── spartantrack.sqlite # SQLite database
├── .github/               # GitHub configuration
│   └── copilot-instructions.md # AI assistant guidelines
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

### Configuration Files

- **`pyproject.toml`**: Modern Python project configuration with dependencies
- **`.gitignore`**: Excludes virtual environments, cache files, and instance data
- **`instance/config.py`**: Production configuration (create as needed)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing code style
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8 Python style guidelines
- Use `black` for consistent formatting
- Add docstrings to functions and classes
- Write meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) web framework
- Database management with [SQLAlchemy](https://www.sqlalchemy.org/)
- Follows [Flask Tutorial](https://flask.palletsprojects.com/tutorial/) patterns
- Spartan-themed design for team identity

## Todo

- Add better user creation with ID card registration
   - add to "member edit" route page and update the 'ID Hash' section.
   - Make sure format for name is correct Start uppercase, auto index of ID Hash
   - need to protect member pages using authentication
   - when 'adding' team make member 'active' by default
   - Create seperate time tracking database to track how long people have been to team meetings (Database done - Cico)
   - cico database formatting, need reporting page
   - By date (who can to which meetings)
   - By user and total time
   - Need to track team meeting time and outreach time
- Add correct authentication around entire application
- Clean up testing
- Update formatting to be smoother, cleaner
- Test and Validate deployment

## Bugs

- Need to fix member delete.  Need to delete entries from cico before removing the use from the members database (Done)
- Converted member id_hash to use sha256 instead of just an integer.


---

**Spartan Teamlog** - Professional team attendance management made simple. 🏛️
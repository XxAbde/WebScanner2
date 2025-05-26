#!/bin/bash
# Database setup script

echo "=== Database Setup for Vulnerability Scanner ==="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting..."
    sudo systemctl start postgresql
fi

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw vulnscanner; echo $?)

if [ $DB_EXISTS -ne 0 ]; then
    echo "📝 Creating database and user..."
    sudo -u postgres psql << EOF
CREATE DATABASE vulnscanner;
CREATE USER vulnuser WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE vulnscanner TO vulnuser;
\q
EOF
    echo "✅ Database created!"
else
    echo "ℹ️  Database already exists"
fi

# Initialize Flask-Migrate
echo "📝 Initializing Flask-Migrate..."
if [ ! -d "migrations" ]; then
    flask db init
fi

# Create migration
echo "📝 Creating initial migration..."
flask db migrate -m "Initial migration - $(date '+%Y-%m-%d %H:%M:%S')"

# Apply migration
echo "📝 Applying migration..."
flask db upgrade

echo "✅ Database setup completed!"
echo ""
echo "Next steps:"
echo "1. Create admin user: python scripts/create_admin.py"
echo "2. (Optional) Seed sample data: python scripts/seed_data.py"
echo "3. Start the application: python run.py"
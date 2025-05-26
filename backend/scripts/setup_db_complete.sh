#!/bin/bash
# Complete database setup with proper permissions

echo "=== Complete Database Setup for Vulnerability Scanner ==="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Set Flask app environment variable
export FLASK_APP=run.py

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting..."
    sudo systemctl start postgresql
fi

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Starting..."
    sudo systemctl start redis-server
fi

echo "📝 Setting up database and user with proper permissions..."

# Drop and recreate database with proper permissions
sudo -u postgres psql << 'EOF'
-- Drop existing database if it exists
DROP DATABASE IF EXISTS vulnscanner;
DROP USER IF EXISTS vulnuser;

-- Create user first
CREATE USER vulnuser WITH PASSWORD 'changeme';

-- Create database and set owner
CREATE DATABASE vulnscanner OWNER vulnuser;

-- Grant additional privileges
GRANT ALL PRIVILEGES ON DATABASE vulnscanner TO vulnuser;
ALTER USER vulnuser CREATEDB;

-- Connect to the database and set up schema permissions
\c vulnscanner

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO vulnuser;
ALTER SCHEMA public OWNER TO vulnuser;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vulnuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vulnuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO vulnuser;

\q
EOF

echo "✅ Database and user created with proper permissions!"

# Test database connection
echo "🔍 Testing database connection..."
if PGPASSWORD=changeme psql -h localhost -U vulnuser -d vulnscanner -c "SELECT current_user, current_database();" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Remove existing migrations if they exist
if [ -d "migrations" ]; then
    echo "📁 Removing existing migrations directory..."
    rm -rf migrations
fi

# Fix migration setup
echo "🔧 Setting up database migrations..."
python scripts/fix_migration.py

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
    echo ""
    echo "📋 Database Information:"
    echo "   Database: vulnscanner"
    echo "   User: vulnuser"
    echo "   Password: changeme"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo ""
    echo "Next steps:"
    echo "1. Create admin user: python scripts/create_admin.py"
    echo "2. (Optional) Seed sample data: python scripts/seed_data.py"
    echo "3. Start the application: python run.py"
else
    echo "❌ Database setup failed"
    exit 1
fi
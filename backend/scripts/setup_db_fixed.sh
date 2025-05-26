#!/bin/bash
# Fixed database setup script

echo "=== Database Setup for Vulnerability Scanner (Fixed) ==="

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

# Check if Redis is running (for rate limiting)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Starting..."
    sudo systemctl start redis-server
fi

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw vulnscanner; echo $?)

if [ $DB_EXISTS -ne 0 ]; then
    echo "📝 Creating database and user..."
    sudo -u postgres psql << EOF
CREATE DATABASE vulnscanner;
CREATE USER vulnuser WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE vulnscanner TO vulnuser;
ALTER USER vulnuser CREATEDB;
\q
EOF
    echo "✅ Database created!"
else
    echo "ℹ️  Database already exists"
fi

# Test database connection
echo "🔍 Testing database connection..."
if PGPASSWORD=changeme psql -h localhost -U vulnuser -d vulnscanner -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Fix migration setup
echo "🔧 Setting up database migrations..."
python scripts/fix_migration.py

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
else
    echo "❌ Database setup failed"
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Create admin user: python scripts/create_admin.py"
echo "2. (Optional) Seed sample data: python scripts/seed_data.py"
echo "3. Start the application: python run.py"
echo ""
echo "📋 Useful commands:"
echo "   - Check database: python run.py --check-only"
echo "   - Run migrations: flask db upgrade"
echo "   - Create new migration: flask db migrate -m 'description'"
#!/bin/bash
# Fix PostgreSQL permissions for vulnuser

echo "🔧 Fixing PostgreSQL Permissions for vulnuser"
echo "=============================================="

# Check current permissions
echo "🔍 Checking current permissions..."
sudo -u postgres psql -d vulnscanner << 'EOF'
-- Check current user permissions
SELECT 
    grantee, 
    table_schema, 
    table_name, 
    privilege_type 
FROM information_schema.table_privileges 
WHERE grantee = 'vulnuser';

-- Check schema permissions
SELECT 
    schema_name,
    schema_owner
FROM information_schema.schemata 
WHERE schema_name = 'public';
EOF

echo ""
echo "🔧 Granting necessary permissions to vulnuser..."

# Fix permissions
sudo -u postgres psql -d vulnscanner << 'EOF'
-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE vulnscanner TO vulnuser;

-- Grant usage and create on public schema
GRANT USAGE ON SCHEMA public TO vulnuser;
GRANT CREATE ON SCHEMA public TO vulnuser;

-- Grant all privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vulnuser;

-- Grant all privileges on all sequences in public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vulnuser;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vulnuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vulnuser;

-- Make vulnuser owner of the database (alternative approach)
-- ALTER DATABASE vulnscanner OWNER TO vulnuser;

-- Verify permissions
\dp
EOF

echo "✅ Permissions updated!"
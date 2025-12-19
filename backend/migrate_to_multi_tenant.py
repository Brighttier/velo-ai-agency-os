#!/usr/bin/env python3
"""
Migration script to add multi-tenant support to existing Velo projects

This script will:
1. Create a default tenant for existing users
2. Associate all existing projects with the default tenant
3. Update user profiles to include tenant_id
"""

import sys
from database.firestore_db import get_db
from datetime import datetime

def migrate_to_multi_tenant():
    """Migrate existing data to multi-tenant structure"""

    db = get_db()

    print("🔄 Starting multi-tenant migration...")
    print()

    # Step 1: Create or get default tenant
    print("Step 1: Creating default tenant/workspace...")

    default_tenant_id = "bright-tier-default"

    # Check if tenant exists
    existing_tenant = db.get_tenant(default_tenant_id)

    if existing_tenant:
        print(f"✅ Default tenant already exists: {existing_tenant['company_name']}")
        tenant_id = existing_tenant['id']
    else:
        # Create default tenant
        tenant_data = {
            "company_name": "Bright Tier Solutions",
            "subdomain": "bright-tier",
            "plan_tier": "enterprise",
            "owner_id": "system",
            "created_by": "migration_script"
        }

        # Manually set the ID for the default tenant
        tenant_ref = db.db.collection('tenants').document(default_tenant_id)
        tenant_data['id'] = default_tenant_id
        tenant_data['created_at'] = datetime.utcnow().isoformat()
        tenant_data['updated_at'] = datetime.utcnow().isoformat()
        tenant_ref.set(tenant_data)

        print(f"✅ Created default tenant: {tenant_data['company_name']} (ID: {default_tenant_id})")
        tenant_id = default_tenant_id

    print()

    # Step 2: Update all existing projects to include tenant_id
    print("Step 2: Migrating projects to default tenant...")

    # Get all projects (without tenant filter)
    all_projects = db.list_projects(tenant_id=None, limit=1000)

    projects_updated = 0
    projects_skipped = 0

    for project in all_projects:
        project_id = project['id']

        # Check if project already has tenant_id
        if project.get('tenant_id'):
            projects_skipped += 1
            continue

        # Update project with tenant_id
        try:
            db.update_project(project_id, {
                'tenant_id': tenant_id,
                'migrated_at': datetime.utcnow().isoformat()
            })
            projects_updated += 1
            print(f"  ✓ Updated project: {project.get('name', 'Unnamed')} (ID: {project_id})")
        except Exception as e:
            print(f"  ✗ Failed to update project {project_id}: {e}")

    print(f"\n✅ Projects migration complete:")
    print(f"   - Updated: {projects_updated}")
    print(f"   - Skipped (already had tenant): {projects_skipped}")
    print()

    # Step 3: Update user profiles
    print("Step 3: Migrating user profiles...")

    # Get all users from Firestore
    users_collection = db.db.collection('users').stream()
    users_updated = 0
    users_skipped = 0

    for user_doc in users_collection:
        user_data = user_doc.to_dict()
        user_id = user_doc.id

        # Check if user already has tenant_id
        if user_data.get('tenant_id'):
            users_skipped += 1
            continue

        # Update user with tenant_id
        try:
            db.update_user(user_id, {
                'tenant_id': tenant_id,
                'role': 'admin',  # Make all existing users admins
                'migrated_at': datetime.utcnow().isoformat()
            })
            users_updated += 1
            print(f"  ✓ Updated user: {user_data.get('email', 'Unknown')} (ID: {user_id})")
        except Exception as e:
            print(f"  ✗ Failed to update user {user_id}: {e}")

    print(f"\n✅ User profiles migration complete:")
    print(f"   - Updated: {users_updated}")
    print(f"   - Skipped (already had tenant): {users_skipped}")
    print()

    # Summary
    print("=" * 60)
    print("🎉 Multi-tenant migration completed successfully!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Tenant: {tenant_id}")
    print(f"  Projects migrated: {projects_updated}")
    print(f"  Users migrated: {users_updated}")
    print()
    print("Next steps:")
    print("  1. Restart the backend server")
    print("  2. All users can now collaborate on shared projects")
    print("  3. Team members with the same tenant_id will see each other's data")
    print()

if __name__ == "__main__":
    try:
        migrate_to_multi_tenant()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

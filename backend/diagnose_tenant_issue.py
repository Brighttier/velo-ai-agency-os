#!/usr/bin/env python3
"""
Diagnostic script to check multi-tenant data sharing issues
"""

from database.firestore_db import get_db
import json

def diagnose_issue():
    """Check current state of tenants, users, and projects"""

    db = get_db()

    print("=" * 70)
    print("MULTI-TENANT DIAGNOSTIC REPORT")
    print("=" * 70)
    print()

    # Check 1: List all tenants
    print("1️⃣  TENANTS")
    print("-" * 70)

    tenants_collection = db.db.collection('tenants').stream()
    tenants = []
    for doc in tenants_collection:
        tenant = doc.to_dict()
        tenant['id'] = doc.id
        tenants.append(tenant)

    if tenants:
        for tenant in tenants:
            print(f"  📦 Tenant ID: {tenant['id']}")
            print(f"     Company: {tenant.get('company_name', 'N/A')}")
            print(f"     Owner: {tenant.get('owner_id', 'N/A')}")
            print(f"     Created: {tenant.get('created_at', 'N/A')}")
            print()
    else:
        print("  ⚠️  NO TENANTS FOUND")
        print()

    # Check 2: List all users
    print("2️⃣  USERS")
    print("-" * 70)

    users_collection = db.db.collection('users').stream()
    users = []
    for doc in users_collection:
        user = doc.to_dict()
        user['uid'] = doc.id
        users.append(user)

    if users:
        for user in users:
            print(f"  👤 User: {user.get('email', 'N/A')}")
            print(f"     UID: {user['uid']}")
            print(f"     Tenant ID: {user.get('tenant_id', '❌ NO TENANT')}")
            print(f"     Role: {user.get('role', 'N/A')}")
            print(f"     Display Name: {user.get('display_name', 'N/A')}")
            print()
    else:
        print("  ⚠️  NO USERS FOUND")
        print()

    # Check 3: List all projects
    print("3️⃣  PROJECTS")
    print("-" * 70)

    all_projects = db.list_projects(tenant_id=None, limit=1000)

    if all_projects:
        projects_by_tenant = {}
        for project in all_projects:
            tenant_id = project.get('tenant_id', 'NO_TENANT')
            if tenant_id not in projects_by_tenant:
                projects_by_tenant[tenant_id] = []
            projects_by_tenant[tenant_id].append(project)

        for tenant_id, projects in projects_by_tenant.items():
            if tenant_id == 'NO_TENANT':
                print(f"  ⚠️  Projects WITHOUT tenant_id: {len(projects)}")
            else:
                print(f"  📁 Projects in tenant '{tenant_id}': {len(projects)}")

            for project in projects:
                print(f"     - {project.get('name', 'Unnamed')}")
                print(f"       ID: {project.get('id')}")
                print(f"       Created by: {project.get('created_by_name', 'Unknown')}")
                print(f"       Tenant: {project.get('tenant_id', '❌ MISSING')}")
            print()
    else:
        print("  ⚠️  NO PROJECTS FOUND")
        print()

    # Analysis
    print("4️⃣  ANALYSIS")
    print("-" * 70)

    issues = []

    # Check if users have different tenant_ids
    if len(users) > 1:
        tenant_ids = set(user.get('tenant_id') for user in users)
        if len(tenant_ids) > 1:
            issues.append(f"❌ ISSUE: Users belong to {len(tenant_ids)} different tenants")
            issues.append(f"   Tenant IDs: {tenant_ids}")
            issues.append(f"   → All team members must have the SAME tenant_id to see each other's data")
        elif None in tenant_ids:
            issues.append(f"❌ ISSUE: Some users don't have a tenant_id assigned")
            issues.append(f"   → Run migration script to assign users to a tenant")
        else:
            issues.append(f"✅ All users belong to the same tenant: {list(tenant_ids)[0]}")

    # Check if projects have tenant_id
    projects_without_tenant = [p for p in all_projects if not p.get('tenant_id')]
    if projects_without_tenant:
        issues.append(f"❌ ISSUE: {len(projects_without_tenant)} projects don't have tenant_id")
        issues.append(f"   → Run migration script to assign projects to a tenant")
    else:
        if all_projects:
            issues.append(f"✅ All {len(all_projects)} projects have tenant_id assigned")

    # Check if users exist
    if not users:
        issues.append(f"❌ ISSUE: No users found in database")
        issues.append(f"   → Users will be created automatically on first login/API call")

    # Check if tenants exist
    if not tenants:
        issues.append(f"❌ ISSUE: No tenants exist")
        issues.append(f"   → Run migration script to create default tenant")

    for issue in issues:
        print(f"  {issue}")
    print()

    # Recommendations
    print("5️⃣  RECOMMENDATIONS")
    print("-" * 70)

    if not tenants or not users or projects_without_tenant or (users and any(not u.get('tenant_id') for u in users)):
        print("  🔧 Run the migration script:")
        print("     python3 backend/migrate_to_multi_tenant.py")
        print()

    if len(users) > 1:
        tenant_ids = set(user.get('tenant_id') for user in users)
        if len(tenant_ids) > 1:
            print("  🔧 To associate all users with the same tenant:")
            print("     1. Choose one tenant_id")
            print("     2. Update each user's tenant_id in Firestore")
            print()
            print("  Example using Firebase Console:")
            for user in users:
                print(f"     - Update user {user.get('email')}: set tenant_id = 'bright-tier-default'")
            print()

    print("  🔧 To verify authentication is working:")
    print("     1. Check browser DevTools Network tab")
    print("     2. Look for API requests with 'Authorization: Bearer ...' header")
    print("     3. Check backend logs for authentication messages")
    print()

    print("  🔧 To manually add Raissa Garcia to your workspace:")
    print("     curl -X POST http://localhost:8000/api/tenant/invite \\")
    print("          -H 'Authorization: Bearer <your-firebase-token>' \\")
    print("          -H 'Content-Type: application/json' \\")
    print("          -d '{\"email\": \"raissa@example.com\"}'")
    print()

    print("=" * 70)
    print("END OF DIAGNOSTIC REPORT")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_issue()

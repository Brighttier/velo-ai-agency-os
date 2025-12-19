#!/usr/bin/env python3
"""
Assign existing users to the default tenant

Run this script after both team members have logged in at least once.
This will update their user profiles to include the tenant_id.
"""

from database.firestore_db import get_db

def assign_users_to_tenant():
    """Assign all existing users to the default tenant"""

    db = get_db()

    print("=" * 70)
    print("ASSIGN USERS TO TENANT")
    print("=" * 70)
    print()

    # Get default tenant
    tenant_id = "bright-tier-default"
    tenant = db.get_tenant(tenant_id)

    if not tenant:
        print("❌ Default tenant 'bright-tier-default' not found!")
        print("   Run: python3 migrate_to_multi_tenant.py first")
        return

    print(f"✅ Found tenant: {tenant['company_name']}")
    print(f"   Tenant ID: {tenant_id}")
    print()

    # Get all users
    users_collection = db.db.collection('users').stream()
    users = []
    for doc in users_collection:
        user = doc.to_dict()
        user['uid'] = doc.id
        users.append(user)

    if not users:
        print("❌ NO USERS FOUND")
        print()
        print("This means no one has logged in yet through Firebase Auth.")
        print()
        print("Next steps:")
        print("  1. Open the frontend app (http://localhost:3000)")
        print("  2. Both you and Raissa need to sign up/login")
        print("  3. After login, user profiles will be created automatically")
        print("  4. Then run this script again to assign them to the tenant")
        print()
        return

    print(f"Found {len(users)} user(s):")
    for user in users:
        print(f"  - {user.get('email', 'Unknown')} (Tenant: {user.get('tenant_id', '❌ None')})")
    print()

    # Assign all users to the tenant
    updated = 0
    skipped = 0

    for user in users:
        uid = user['uid']
        email = user.get('email', 'Unknown')

        if user.get('tenant_id') == tenant_id:
            print(f"  ⏭️  Skipping {email} - already in tenant")
            skipped += 1
            continue

        try:
            db.update_user(uid, {
                'tenant_id': tenant_id,
                'role': 'admin'  # Make all users admins
            })
            print(f"  ✅ Assigned {email} to tenant '{tenant_id}' as admin")
            updated += 1
        except Exception as e:
            print(f"  ❌ Failed to update {email}: {e}")

    print()
    print("=" * 70)
    print(f"✅ Updated {updated} user(s)")
    print(f"   Skipped {skipped} user(s) (already assigned)")
    print()
    print("Result:")
    print(f"  All users are now members of '{tenant['company_name']}'")
    print(f"  They can see each other's projects, contacts, and pipeline data!")
    print()
    print("Next Steps:")
    print("  1. Restart the frontend (refresh the browser)")
    print("  2. Both users should now see shared data")
    print("  3. Create a project as one user - the other should see it")
    print("=" * 70)

if __name__ == "__main__":
    assign_users_to_tenant()

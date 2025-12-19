#!/usr/bin/env python3
"""
Create user profiles for team members and associate them with the default tenant
"""

from database.firestore_db import get_db
from datetime import datetime

def create_team_users():
    """Create user profiles for Wolf and Raissa Garcia"""

    db = get_db()

    print("🔧 Creating team user profiles...")
    print()

    # Get the default tenant
    tenant_id = "bright-tier-default"
    tenant = db.get_tenant(tenant_id)

    if not tenant:
        print("❌ Default tenant not found. Run migrate_to_multi_tenant.py first!")
        return

    print(f"✅ Found tenant: {tenant['company_name']}")
    print()

    # Define team members
    # NOTE: Replace these with actual Firebase UIDs and emails
    team_members = [
        {
            "uid": "wolf-user-id",  # Replace with actual Firebase UID after first login
            "email": "wolf@brighttier.com",  # Replace with your actual email
            "display_name": "Wolf",
            "role": "admin"
        },
        {
            "uid": "raissa-user-id",  # Replace with Raissa's Firebase UID
            "email": "raissa.garcia@brighttier.com",  # Replace with Raissa's actual email
            "display_name": "Raissa Garcia",
            "role": "admin"
        }
    ]

    print("📋 Team Members to Create:")
    for member in team_members:
        print(f"   - {member['display_name']} ({member['email']})")
    print()

    # Create user profiles
    created = 0
    for member in team_members:
        try:
            user_data = {
                "uid": member["uid"],
                "email": member["email"],
                "display_name": member["display_name"],
                "tenant_id": tenant_id,
                "role": member["role"]
            }

            db.create_user(user_data)
            print(f"✅ Created user: {member['display_name']}")
            created += 1
        except Exception as e:
            print(f"❌ Failed to create {member['display_name']}: {e}")

    print()
    print("=" * 70)
    print(f"✅ Successfully created {created} user profiles")
    print(f"   All users are now associated with tenant: {tenant_id}")
    print()
    print("Next Steps:")
    print("  1. Both users need to log in through Firebase Auth")
    print("  2. After login, their Firebase UID will be available")
    print("  3. Update the UIDs in this script if needed")
    print("  4. Re-run this script to update user profiles")
    print()
    print("IMPORTANT:")
    print("  The system will auto-create user profiles on first API call,")
    print("  but they won't have tenant_id by default.")
    print("  You need to either:")
    print("    A) Update UIDs in this script and re-run it")
    print("    B) Manually update user profiles in Firestore after first login")
    print("=" * 70)

if __name__ == "__main__":
    create_team_users()

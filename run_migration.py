#!/usr/bin/env python3
"""
Simple script to run the image storage migration.
Run this script to convert from file-based image storage to database binary storage.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the migration
from migrate_to_binary_images import migrate_images_to_database, verify_migration

if __name__ == "__main__":
    print("🔄 Starting Image Storage Migration")
    print("=" * 50)
    
    try:
        # Run the migration
        success = migrate_images_to_database()
        
        if success:
            # Verify the migration
            verify_migration()
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Next steps:")
            print("1. Test your application to ensure images load correctly")
            print("2. If everything works, you can optionally remove the old image files")
            print("3. Consider backing up your database before making further changes")
            
        else:
            print("\n❌ Migration failed!")
            print("Please check the error messages above and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during migration: {str(e)}")
        sys.exit(1)

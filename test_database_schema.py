#!/usr/bin/env python3
"""
Test script to verify the database schema is working correctly
"""

import sys
import os
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine

def test_database_schema():
    """Test that the database schema is correctly set up"""
    
    print("🔍 Testing Database Schema")
    print("=" * 40)
    
    try:
        with engine.connect() as conn:
            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'questions'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            print("📋 Current table structure:")
            print("-" * 40)
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  {col[0]:<15} {col[1]:<15} {nullable}")
            
            print("\n✅ Required columns check:")
            column_names = [col[0] for col in columns]
            
            required_new_columns = ['image_data', 'image_filename']
            for col in required_new_columns:
                if col in column_names:
                    print(f"  ✓ {col} - Present")
                else:
                    print(f"  ✗ {col} - Missing")
            
            # Check if image_path is nullable now
            image_path_nullable = None
            for col in columns:
                if col[0] == 'image_path':
                    image_path_nullable = col[2] == "YES"
                    break
            
            if image_path_nullable is not None:
                if image_path_nullable:
                    print(f"  ✓ image_path - Now nullable (good for new records)")
                else:
                    print(f"  ⚠️ image_path - Still NOT NULL (may cause issues)")
            
            print("\n🧪 Testing insert capability:")
            
            # Test if we can insert a record with the new schema
            test_data = {
                'image_data': b'test_binary_data',
                'image_filename': 'test.jpg',
                'question': 'Test question?',
                'answer': 'Test answer'
            }
            
            # Try to insert (but rollback to not affect actual data)
            trans = conn.begin()
            try:
                result = conn.execute(text("""
                    INSERT INTO questions (image_data, image_filename, question, answer) 
                    VALUES (:image_data, :image_filename, :question, :answer) 
                    RETURNING id
                """), test_data)
                
                new_id = result.fetchone()[0]
                print(f"  ✓ Insert test successful (ID: {new_id})")
                
                # Rollback to not keep test data
                trans.rollback()
                print(f"  ✓ Test data rolled back")
                
            except Exception as e:
                trans.rollback()
                print(f"  ✗ Insert test failed: {e}")
                return False
            
            print("\n🎉 Database schema is ready for binary image storage!")
            return True
            
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_schema()
    if not success:
        sys.exit(1)
    else:
        print("\n" + "=" * 40)
        print("✅ All tests passed! Ready to use the application.")

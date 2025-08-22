#!/usr/bin/env python3
"""
Migration script to convert image storage from file system to database binary storage.
This script will:
1. Create new database columns for binary image storage
2. Read existing image files and store them as binary data in the database
3. Update the database schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import get_db, engine
import models
import services

def migrate_images_to_database():
    """Migrate existing images from file system to database binary storage"""
    
    print("Starting migration from file system to database binary storage...")
    
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # First, add new columns to existing table if they don't exist
        print("Adding new columns to database...")
        
        # Check if new columns exist (PostgreSQL version)
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'questions'
        """))
        columns = [row[0] for row in result.fetchall()]

        if 'image_data' not in columns:
            db.execute(text("ALTER TABLE questions ADD COLUMN image_data BYTEA"))
            print("Added image_data column")

        if 'image_filename' not in columns:
            db.execute(text("ALTER TABLE questions ADD COLUMN image_filename TEXT"))
            print("Added image_filename column")

        # Remove NOT NULL constraint from old image_path column to allow new records
        try:
            db.execute(text("ALTER TABLE questions ALTER COLUMN image_path DROP NOT NULL"))
            print("Removed NOT NULL constraint from image_path column")
        except Exception as e:
            print(f"Note: Could not remove NOT NULL constraint (may already be removed): {e}")

        db.commit()
        
        # Get all existing questions
        questions = db.query(models.Question).all()
        print(f"Found {len(questions)} questions to migrate")
        
        migrated_count = 0
        error_count = 0
        
        for question in questions:
            try:
                # Skip if already migrated (has image_data)
                if hasattr(question, 'image_data') and question.image_data:
                    print(f"Question {question.id} already migrated, skipping...")
                    continue
                
                # Construct file path from old image_path
                if hasattr(question, 'image_path'):
                    image_file_path = os.path.join("static", "uploads", question.image_path)
                    
                    if os.path.exists(image_file_path):
                        # Read image file as binary
                        with open(image_file_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Update question with binary data
                        db.execute(
                            text("UPDATE questions SET image_data = :image_data, image_filename = :filename WHERE id = :id"),
                            {
                                "image_data": image_data,
                                "filename": question.image_path,
                                "id": question.id
                            }
                        )
                        
                        migrated_count += 1
                        print(f"Migrated question {question.id}: {question.image_path}")
                    else:
                        print(f"Warning: Image file not found for question {question.id}: {image_file_path}")
                        error_count += 1
                else:
                    print(f"Warning: Question {question.id} has no image_path")
                    error_count += 1
                    
            except Exception as e:
                print(f"Error migrating question {question.id}: {str(e)}")
                error_count += 1
        
        db.commit()
        
        print(f"\nMigration completed!")
        print(f"Successfully migrated: {migrated_count} questions")
        print(f"Errors encountered: {error_count} questions")
        
        # Optionally remove old column (commented out for safety)
        # print("Removing old image_path column...")
        # db.execute(text("ALTER TABLE questions DROP COLUMN image_path"))
        # db.commit()
        # print("Old column removed")
        
        print("\nNote: Old image_path column is preserved for safety.")
        print("You can manually remove it later if everything works correctly.")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def verify_migration():
    """Verify that the migration was successful"""
    print("\nVerifying migration...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        questions = db.query(models.Question).all()
        
        for question in questions:
            if hasattr(question, 'image_data') and question.image_data:
                print(f"✓ Question {question.id}: Has binary data ({len(question.image_data)} bytes)")
            else:
                print(f"✗ Question {question.id}: Missing binary data")
                
    except Exception as e:
        print(f"Verification failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Image Storage Migration Tool")
    print("=" * 40)
    
    # Check if static/uploads directory exists
    if not os.path.exists("static/uploads"):
        print("Error: static/uploads directory not found!")
        print("Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Run migration
    if migrate_images_to_database():
        verify_migration()
        print("\n" + "=" * 40)
        print("Migration completed successfully!")
        print("You can now start your application with the new binary image storage.")
    else:
        print("\n" + "=" * 40)
        print("Migration failed! Please check the errors above.")
        sys.exit(1)

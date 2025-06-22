#!/usr/bin/env python3
"""
Script to clear the database and start fresh
"""

import os
from dotenv import load_dotenv
from mongoDB import MongoDBManager

# Load environment variables
load_dotenv()

def clear_database():
    """Clear the tracks collection to start fresh"""
    
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        print("❌ MONGODB_URI environment variable not set.")
        return
    
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager(connection_string, "spotilike", "tracks")
        
        if not mongo_manager.connect():
            print("❌ Failed to connect to MongoDB")
            return
        
        # Count documents before clearing
        count_before = mongo_manager.count_documents()
        print(f"📊 Found {count_before} documents in collection")
        
        if count_before > 0:
            # Clear the collection
            print("🗑️ Clearing collection...")
            mongo_manager.drop_collection()
            print("✅ Collection cleared successfully")
        else:
            print("ℹ️ Collection is already empty")
        
        # Verify it's empty
        count_after = mongo_manager.count_documents()
        print(f"📊 Collection now has {count_after} documents")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    
    finally:
        if 'mongo_manager' in locals() and mongo_manager.client:
            mongo_manager.disconnect()
            print("🔌 Disconnected from MongoDB")

if __name__ == "__main__":
    print("🧹 Clearing database to start fresh...")
    clear_database()
    print("✅ Database cleared! You can now start fresh.") 
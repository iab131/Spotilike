import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class MongoDBManager:
    def __init__(self, connection_string=None, database_name="spotilike", collection_name="users"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string (str): MongoDB connection string
            database_name (str): Name of the database
            collection_name (str): Name of the collection
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI')
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        
        if not self.connection_string:
            raise ValueError("MongoDB connection string is required. Set MONGODB_URI environment variable or pass connection_string parameter.")
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB!")
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    def insert_one(self, document):
        """
        Insert a single document
        
        Args:
            document (dict): Document to insert
            
        Returns:
            ObjectId: ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow()
            
            result = self.collection.insert_one(document)
            print(f"✅ Document inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ Error inserting document: {e}")
            return None
    
    def insert_many(self, documents):
        """
        Insert multiple documents
        
        Args:
            documents (list): List of documents to insert
            
        Returns:
            list: List of inserted document IDs
        """
        try:
            # Add timestamp to each document if not present
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = datetime.utcnow()
            
            result = self.collection.insert_many(documents)
            print(f"✅ {len(result.inserted_ids)} documents inserted")
            return result.inserted_ids
        except Exception as e:
            print(f"❌ Error inserting documents: {e}")
            return []
    
    def find_one(self, filter_query=None):
        """
        Find a single document
        
        Args:
            filter_query (dict): Query filter
            
        Returns:
            dict: Found document or None
        """
        try:
            document = self.collection.find_one(filter_query or {})
            if document:
                print(f"✅ Document found: {document}")
            else:
                print("ℹ️ No document found")
            return document
        except Exception as e:
            print(f"❌ Error finding document: {e}")
            return None
    
    def find_many(self, filter_query=None, limit=None, sort_by=None):
        """
        Find multiple documents
        
        Args:
            filter_query (dict): Query filter
            limit (int): Maximum number of documents to return
            sort_by (tuple): Sort criteria (field, direction)
            
        Returns:
            list: List of found documents
        """
        try:
            query = self.collection.find(filter_query or {})
            
            if sort_by:
                query = query.sort(sort_by[0], sort_by[1])
            
            if limit:
                query = query.limit(limit)
            
            documents = list(query)
            print(f"✅ Found {len(documents)} documents")
            return documents
        except Exception as e:
            print(f"❌ Error finding documents: {e}")
            return []
    
    def update_one(self, filter_query, update_data, upsert=False):
        """
        Update a single document
        
        Args:
            filter_query (dict): Query filter
            update_data (dict): Update data
            upsert (bool): Create document if it doesn't exist
            
        Returns:
            bool: Success status
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                filter_query,
                {'$set': update_data},
                upsert=upsert
            )
            
            if result.matched_count > 0:
                print(f"✅ Updated {result.modified_count} document(s)")
            elif result.upserted_id:
                print(f"✅ Created new document with ID: {result.upserted_id}")
            else:
                print("ℹ️ No documents matched the filter")
            
            return True
        except Exception as e:
            print(f"❌ Error updating document: {e}")
            return False
    
    def update_many(self, filter_query, update_data):
        """
        Update multiple documents
        
        Args:
            filter_query (dict): Query filter
            update_data (dict): Update data
            
        Returns:
            bool: Success status
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_many(
                filter_query,
                {'$set': update_data}
            )
            
            print(f"✅ Updated {result.modified_count} document(s)")
            return True
        except Exception as e:
            print(f"❌ Error updating documents: {e}")
            return False
    
    def delete_one(self, filter_query):
        """
        Delete a single document
        
        Args:
            filter_query (dict): Query filter
            
        Returns:
            bool: Success status
        """
        try:
            result = self.collection.delete_one(filter_query)
            if result.deleted_count > 0:
                print(f"✅ Deleted {result.deleted_count} document(s)")
            else:
                print("ℹ️ No documents matched the filter")
            return True
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
    
    def delete_many(self, filter_query):
        """
        Delete multiple documents
        
        Args:
            filter_query (dict): Query filter
            
        Returns:
            bool: Success status
        """
        try:
            result = self.collection.delete_many(filter_query)
            print(f"✅ Deleted {result.deleted_count} document(s)")
            return True
        except Exception as e:
            print(f"❌ Error deleting documents: {e}")
            return False
    
    def count_documents(self, filter_query=None):
        """
        Count documents in collection
        
        Args:
            filter_query (dict): Query filter
            
        Returns:
            int: Number of documents
        """
        try:
            count = self.collection.count_documents(filter_query or {})
            print(f"📊 Total documents: {count}")
            return count
        except Exception as e:
            print(f"❌ Error counting documents: {e}")
            return 0
    
    def drop_collection(self):
        """Drop the entire collection"""
        try:
            self.collection.drop()
            print("🗑️ Collection dropped successfully")
            return True
        except Exception as e:
            print(f"❌ Error dropping collection: {e}")
            return False

def main():
    """Example usage of MongoDB operations"""
    
    # Initialize MongoDB manager with your actual connection string
    connection_string = os.getenv('MONGODB_URI')
    
    try:
        # Create MongoDB manager instance
        mongo_manager = MongoDBManager(connection_string, "spotilike", "users")
        
        # Connect to MongoDB
        if not mongo_manager.connect():
            return
        
        # Example operations
        
        # 1. Insert a single document
        print("\n=== INSERTING SINGLE DOCUMENT ===")
        user_doc = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "preferences": ["rock", "jazz", "classical"]
        }
        mongo_manager.insert_one(user_doc)
        
        # 2. Insert multiple documents
        print("\n=== INSERTING MULTIPLE DOCUMENTS ===")
        users = [
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25, "preferences": ["pop", "electronic"]},
            {"name": "Bob Johnson", "email": "bob@example.com", "age": 35, "preferences": ["country", "folk"]},
            {"name": "Alice Brown", "email": "alice@example.com", "age": 28, "preferences": ["hip-hop", "r&b"]}
        ]
        mongo_manager.insert_many(users)
        
        # 3. Find documents
        print("\n=== FINDING DOCUMENTS ===")
        # Find one document
        mongo_manager.find_one({"name": "John Doe"})
        
        # Find all documents
        all_users = mongo_manager.find_many()
        
        # Find documents with filter
        young_users = mongo_manager.find_many({"age": {"$lt": 30}})
        
        # 4. Update documents
        print("\n=== UPDATING DOCUMENTS ===")
        mongo_manager.update_one(
            {"name": "John Doe"},
            {"age": 31, "preferences": ["rock", "jazz", "classical", "blues"]}
        )
        
        # 5. Count documents
        print("\n=== COUNTING DOCUMENTS ===")
        mongo_manager.count_documents()
        
        # 6. Delete documents
        print("\n=== DELETING DOCUMENTS ===")
        mongo_manager.delete_one({"name": "Alice Brown"})
        
        # 7. Find updated documents
        print("\n=== FINDING UPDATED DOCUMENTS ===")
        mongo_manager.find_many(sort_by=("created_at", -1))
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Disconnect from MongoDB
        if 'mongo_manager' in locals():
            mongo_manager.disconnect()

if __name__ == "__main__":
    main() 
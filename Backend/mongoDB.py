import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class MongoDBManager:
    def __init__(self, connection_string=None, database_name="spotilike", collection_name="tracks"):
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
            result = self.collection.update_one(
                filter_query,
                update_data,
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
            result = self.collection.update_many(
                filter_query,
                update_data
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

    def update_track_score(self, track_id, score_change, emotion):
        """
        Updates the score for a track with emotion tracking.
        Each emotion (happy, sad, angry, surprise, fear, disgust, neutral, skipped) 
        is tracked separately with its own count.

        Args:
            track_id (str): The ID of the track.
            score_change (int): +1 for positive emotion, -1 for negative emotion.
            emotion (str): The emotion to track (happy, sad, angry, surprise, fear, disgust, neutral, skipped).
        """
        if score_change not in [1, -1]:
            print("❌ Invalid score_change value. Must be 1 or -1.")
            return False
            
        try:
            query = {'track_id': track_id}
            
            # Check if document already exists
            existing_doc = self.collection.find_one(query)
            
            if existing_doc:
                print(f"📄 Found existing document for track {track_id}")
                print(f"📄 Existing document structure: {list(existing_doc.keys())}")
                
                # Check if the document has the new emotion structure
                emotion_field = f'emotion_{emotion}'
                has_emotion_field = emotion_field in existing_doc
                
                if has_emotion_field:
                    # Document exists and has the new structure - just increment
                    update = {
                        '$inc': {
                            'total_score': score_change,
                            emotion_field: 1
                        }
                    }
                    
                    result = self.collection.update_one(query, update)
                    
                    if result.modified_count > 0:
                        print(f"✅ Updated track '{track_id}' - added {emotion} (+{score_change})")
                    else:
                        print(f"ℹ️ No change for track '{track_id}'.")
                else:
                    # Document exists but has old structure - migrate it
                    print(f"🔄 Migrating old document structure for track {track_id}")
                    
                    # Initialize all emotion fields
                    all_emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral', 'skipped']
                    emotion_updates = {}
                    for emo in all_emotions:
                        emotion_updates[f'emotion_{emo}'] = 0
                    
                    # Set current emotion to 1
                    emotion_updates[emotion_field] = 1
                    
                    # Update with new structure
                    update = {
                        '$set': emotion_updates,
                        '$inc': {
                            'total_score': score_change
                        }
                    }
                    
                    result = self.collection.update_one(query, update)
                    
                    if result.modified_count > 0:
                        print(f"✅ Migrated and updated track '{track_id}' - added {emotion} (+{score_change})")
                    else:
                        print(f"❌ Failed to migrate track '{track_id}'")
            else:
                # Document doesn't exist - create new document with all emotions initialized
                print(f"🆕 Creating new document for track {track_id}")
                all_emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral', 'skipped']
                
                # Initialize all emotion counts to 0
                emotion_init = {}
                for emo in all_emotions:
                    emotion_init[f'emotion_{emo}'] = 0
                
                # Set the current emotion to 1
                emotion_field = f'emotion_{emotion}'
                emotion_init[emotion_field] = 1
                
                # Create new document
                new_doc = {
                    'track_id': track_id,
                    'total_score': score_change,
                    **emotion_init
                }
                
                result = self.collection.insert_one(new_doc)
                
                if result.inserted_id:
                    print(f"✅ Created new track '{track_id}' with {emotion}: {score_change} and initialized all emotions")
                else:
                    print(f"❌ Failed to create new track '{track_id}'")

            return True
        except Exception as e:
            print(f"❌ Error updating track score: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Example usage of the track score update functionality with multi-emotion tracking"""
    
    # IMPORTANT: Create a .env file in your project root and add your MongoDB connection string:
    # MONGODB_URI="your_mongodb_connection_string"
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        print("❌ MONGODB_URI environment variable not set. Please set it in a .env file.")
        return

    try:
        # Initialize with the 'tracks' collection
        mongo_manager = MongoDBManager(connection_string, "spotilike", "tracks")
        
        if not mongo_manager.connect():
            return

        # Drop the collection for a clean test run
        print("\n=== DROPPING COLLECTION FOR A FRESH START ===")
        mongo_manager.drop_collection()

        print("\n=== UPDATING TRACK SCORES WITH MULTI-EMOTION TRACKING ===")
        
        # Example Track IDs from Spotify
        track_id_1 = "4cOdK2wGLETOMsV3g9B1rA"  # "Blinding Lights" by The Weeknd
        track_id_2 = "0e7ipj03S05BNilyu5bRzt"  # "As It Was" by Harry Styles
        
        # --- Scenario 1: User is HAPPY with song 1 ---
        print(f"\n1. User is HAPPY with song: {track_id_1}")
        mongo_manager.update_track_score(track_id_1, 1, "happy")
        
        # --- Scenario 2: User is HAPPY again with song 1 ---
        print(f"\n2. User is HAPPY again with song: {track_id_1}")
        mongo_manager.update_track_score(track_id_1, 1, "happy")
        
        # --- Scenario 3: User is SAD with song 1 ---
        print(f"\n3. User is SAD with song: {track_id_1}")
        mongo_manager.update_track_score(track_id_1, -1, "sad")
        
        # --- Scenario 4: User SKIPS song 1 ---
        print(f"\n4. User SKIPS song: {track_id_1}")
        mongo_manager.update_track_score(track_id_1, -1, "skipped")
        
        # --- Scenario 5: User is ANGRY with song 2 ---
        print(f"\n5. User is ANGRY with song: {track_id_2}")
        mongo_manager.update_track_score(track_id_2, -1, "angry")
        
        # --- Scenario 6: User is SURPRISED with song 2 ---
        print(f"\n6. User is SURPRISED with song: {track_id_2}")
        mongo_manager.update_track_score(track_id_2, 1, "surprise")
        
        # --- Scenario 7: Let's see the results ---
        print("\n=== FINAL TRACK SCORES WITH EMOTION BREAKDOWN ===")
        all_tracks = mongo_manager.find_many(sort_by=("total_score", -1)) # Sort by total_score descending
        if all_tracks:
            # Using json.dumps for pretty printing BSON/ObjectId
            print(json.dumps(all_tracks, indent=2, default=str))

    except Exception as e:
        print(f"❌ An error occurred in main: {e}")
    
    finally:
        # Disconnect from MongoDB
        if 'mongo_manager' in locals() and mongo_manager.client:
            mongo_manager.disconnect()

if __name__ == "__main__":
    main() 
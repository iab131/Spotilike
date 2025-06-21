import os

def main():
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        print("❌ MONGODB_URI environment variable not set. Please set it in a .env file.")
        return

    mongo_manager = MongoDBManager(connection_string, "spotilike", "tracks")

    if not mongo_manager.connect():
        return

    mongo_manager.drop_collection() #delete all data in the collection

    track_id = "123"
    mongo_manager.update_track_score(track_id, 1)  # Happy +1
    mongo_manager.update_track_score(track_id, -1)  # Happy +1

if __name__ == "__main__":
    main() 
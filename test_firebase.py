from config import bucket

def list_files():
    blobs = bucket.list_blobs()
    for blob in blobs:
        print(blob.name)

if __name__ == "__main__":
    list_files()

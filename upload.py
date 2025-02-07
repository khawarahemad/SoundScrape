import boto3
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Cloudflare R2 Configuration (Update These)
R2_ACCESS_KEY = "39a8988d7c87584b9e19bd4df3bca866"
R2_SECRET_KEY = "ded4921da3aeb347da5df97349053899820e899dd804c1503523b5e416b519a0"
R2_ENDPOINT = "https://171a829e0ca19fc442388470df732c5f.r2.cloudflarestorage.com"
BUCKET_NAME = "musify"

# Initialize Boto3 Client
try:
    session = boto3.session.Session()
    s3_client = session.client(
        service_name="s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
    )
    print("✅ Connected to Cloudflare R2 successfully.")
except Exception as e:
    print(f"❌ Failed to connect to Cloudflare R2: {e}")
    exit(1)

# Define local folder path
local_folder = "/Users/khawarahemadkhan/web pages/musify script/songs"

# Check if folder exists
if not os.path.exists(local_folder):
    print(f"❌ Error: Folder '{local_folder}' not found.")
    exit(1)

# Get all files to upload
files_to_upload = []
for root, _, files in os.walk(local_folder):
    for file in files:
        files_to_upload.append(os.path.join(root, file))

total_files = len(files_to_upload)
if total_files == 0:
    print("⚠️ No files found in the folder. Exiting...")
    exit(1)

print(f"🔍 Found {total_files} files to upload.")

uploaded_files = 0  # Counter for uploaded files
lock = Lock()  # To prevent race conditions when updating the counter

# Function to upload a single file
def upload_file(file_path):
    global uploaded_files
    object_key = os.path.relpath(file_path, local_folder)  # Preserve folder structure
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, f"songs/{object_key}")

        # Update progress
        with lock:
            uploaded_files += 1
            print(f"✅ Uploaded {uploaded_files}/{total_files}: {file_path}")
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {e}")

# Use ThreadPoolExecutor for parallel uploads
max_workers = 5  # Adjust based on your system
print("🚀 Uploading files in parallel...")
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(upload_file, file) for file in files_to_upload]

    # Wait for all uploads to complete
    for future in as_completed(futures):
        future.result()  # This ensures any errors in uploads are caught

print("🎉 All files uploaded successfully!")

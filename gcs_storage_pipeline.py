import os
import sys
import shutil
import logging
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv 
from google.oauth2 import service_account
from google.cloud.storage import Client, transfer_manager


# Setup strict logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_google_key_dict() -> Dict[str, str]:
    """Retrieves credentials with strict checking."""
    keys = [
        'type', 'project_id', 'private_key_id', 'private_key', 
        'client_email', 'client_id', 'auth_uri', 'token_uri'
    ]
    try:
        return {k: os.environ[f"DESTINATION__GOOGLE__CREDENTIALS__{k.upper()}"] for k in keys}
    except KeyError as e:
        logger.critical(f"Missing mandatory environment variable: {e}")
        sys.exit(1)

def upload_generated_data(source_dir: str) -> None:
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source directory does not exist: {source_dir}")
        return

    # Initialize Client
    creds_dict = get_google_key_dict()    
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    storage_client = Client(credentials=creds, project=creds_dict['project_id'])

    # Bucket cleanup
    raw_url = os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL", "")
    bucket_name = raw_url.replace("gs://", "").strip("/")
    if not bucket_name:
        raise ValueError("BUCKET_URL is not set or invalid.")
    
    bucket = storage_client.bucket(bucket_name)

    # Gather files
    file_paths = [
        str(p.relative_to(source_path)) 
        for p in source_path.rglob("*") if p.is_file()
    ]

    # Prefix should be the folder name only to avoid nested path mess
    destination_prefix = f"{source_path.name}/" 

    logger.info(f"Uploading {len(file_paths)} files to gs://{bucket_name}/{destination_prefix}...")

    results = transfer_manager.upload_many_from_filenames(
        bucket, 
        file_paths, 
        source_directory=str(source_path),
        blob_name_prefix=destination_prefix, # keeps the 'output' folder wrapper
        max_workers=8 
    )

    # 2. Strict Success Evaluation
    errors = [res for res in results if isinstance(res, Exception)]
    
    if not errors and len(results) > 0:
        logger.info(f"Successfully uploaded {len(results)} files. Starting cleanup...")
        
        # 3. Defensive Deletion
        # Check that we aren't deleting something dangerous (like root or a parent)
        if source_path == Path.home() or source_path == Path("/"):
             logger.critical(f"REFUSING TO DELETE SENSITIVE PATH: {source_path}")
             return

        try:
            # shutil.rmtree is recursive and final. Use with care.
            shutil.rmtree(source_path)
            logger.info(f"Local directory {source_path} successfully deleted.")
        except Exception as e:
            # We don't sys.exit(1) here because the DATA LOAD succeeded.
            # We just log a high-priority error for the dev to clean up disk space later.
            logger.error(f"Cleanup failed for {source_path}: {e}")
            
    elif len(results) == 0:
        logger.warning("No files were found to upload. Skipping cleanup to be safe.")
    else:
        logger.error(f"Cleanup aborted. {len(errors)} files failed to upload.")
        # Logging individual errors for the orchestrator
        for i, error in enumerate(errors[:5]): # Log first 5 to avoid log spam
            logger.error(f"Sample error {i+1}: {error}")

if __name__ == "__main__":
    load_dotenv()
    upload_generated_data("2026-02-26_output")


# def get_google_key_dict() -> dict:
#     return {
#         'type' :  os.getenv("DESTINATION__GOOGLE__CREDENTIALS__TYPE"), 
#         'project_id' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__PROJECT_ID") ,
#         'private_key_id' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__PRIVATE_KEY_ID") ,
#         'private_key' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__PRIVATE_KEY") ,
#         'client_email' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__CLIENT_EMAIL") ,
#         'client_id' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__CLIENT_ID") ,
#         'auth_uri' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__AUTH_URI") ,
#         'token_uri' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__TOKEN_URI") ,
#         'auth_provider_x509_cert_url' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__AUTH_PROVIDER_X509_CERT_URL"),
#         'client_x509_cert_url' : os.getenv("DESTINATION__GOOGLE__CREDENTIALS__CLIENT_X509_CERT_URL")
#     }


# def upload_generated_data(source_dir: str) -> None:
#     creds_dict = get_google_key_dict()    
#     creds = service_account.Credentials.from_service_account_info(creds_dict)
#     storage_client = Client(credentials=creds, project=creds_dict['project_id'])


#     bucket_name = os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL").replace("gs://", "").strip("/")
#     bucket = storage_client.bucket(bucket_name)

#     directory_path = Path(source_dir)
    
#     file_paths = [
#         str(p.relative_to(directory_path)) 
#         for p in directory_path.rglob("*") if p.is_file()
#     ]

#     # Optional: Add a prefix for 'output' folder name to appear in GCS under the bucket root
#     # Otherwise, the contents of 'output' will sit in the bucket root.
#     destination_prefix = f"{source_dir}/" 

#     results = transfer_manager.upload_many_from_filenames(
#         bucket, 
#         file_paths, 
#         source_directory=source_dir,
#         blob_name_prefix=destination_prefix, # keeps the 'output' folder wrapper
#         max_workers=8 
#     )

#     for result in results:
#         if isinstance(result, Exception):
#             print(f"Failed: {result}")

# if __name__=="__main__":
#     load_dotenv()
#     bucket_name = os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL").replace("gs://", "").strip("/")
#     upload_generated_data("2026-02-26_output")
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

    # Success Evaluation
    errors = [res for res in results if isinstance(res, Exception)]
    
    if not errors and len(results) > 0:
        logger.info(f"Successfully uploaded {len(results)} files. Starting cleanup...")
        
    # Defensive Deletion
        # Check that we aren't deleting something dangerous (like root or a parent)
        if source_path == Path.home() or source_path == Path("/"):
             logger.critical(f"REFUSING TO DELETE SENSITIVE PATH: {source_path}")
             return

        try:
            shutil.rmtree(source_path)
            logger.info(f"Local directory {source_path} successfully deleted.")
        except Exception as e:
            logger.error(f"Cleanup failed for {source_path}: {e}")
            
    elif len(results) == 0:
        logger.warning("No files were found to upload. Skipping cleanup to be safe.")
    else:
        logger.error(f"Cleanup aborted. {len(errors)} files failed to upload.")
        for i, error in enumerate(errors[:5]):
            logger.error(f"Sample error {i+1}: {error}")

if __name__ == "__main__":
    load_dotenv()
    upload_generated_data("2026-02-26_output")

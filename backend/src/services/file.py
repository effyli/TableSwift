from fastapi import UploadFile, HTTPException
from uuid import uuid4, UUID
from pathlib import Path
import os
import asyncio

async def save_uploaded_file(file: UploadFile, user_id: UUID) -> tuple[str, str]:
    """
    Save the uploaded file to the user's directory and return the file path and name.
    """
    # Reset file position for reading
    await file.seek(0)

    # Create user directory if it doesn't exist
    user_dir = Path(f"data/users/{user_id}/files")
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename while preserving the original extension
    original_extension = Path(file.filename).suffix
    unique_filename = f"{uuid4()}{original_extension}"
    file_path = user_dir / unique_filename
    
    # Save the file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
        
    return str(file_path), file.filename


async def delete_file(file_path: str) -> None:
    """
    Delete a file and clean up empty directories.
    If the user's directory becomes empty after file deletion, it will also be removed.
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, 
                detail="File not found"
            )

        # Get the directory path before deleting the file
        dir_path = os.path.dirname(file_path)
        
        # Delete the file
        await asyncio.to_thread(os.remove, file_path)
        
        # Check if directory is empty
        remaining_files = await asyncio.to_thread(os.listdir, dir_path)
        if not remaining_files:
            # If directory is empty, delete it
            try:
                await asyncio.to_thread(os.rmdir, dir_path)
                
                # Also try to remove parent "files" directory if it's empty
                parent_dir = os.path.dirname(dir_path)
                if os.path.exists(parent_dir):
                    parent_files = await asyncio.to_thread(os.listdir, parent_dir)
                    if not parent_files:
                        await asyncio.to_thread(os.rmdir, parent_dir)
                        
                        # Finally, try to remove the user directory if it's empty
                        user_dir = os.path.dirname(parent_dir)
                        if os.path.exists(user_dir):
                            user_files = await asyncio.to_thread(os.listdir, user_dir)
                            if not user_files:
                                await asyncio.to_thread(os.rmdir, user_dir)
                
            except Exception as dir_error:
                print(f"Warning: Could not remove empty directory: {str(dir_error)}")
                # Don't raise an exception here as the file deletion was successful
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
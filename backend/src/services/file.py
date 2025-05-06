from fastapi import UploadFile, HTTPException
from uuid import uuid4, UUID
from pathlib import Path
import os
import asyncio
import pandas as pd
from ..models.file import CreateFile, File
from ..database import get_db

async def save_file_db(file: CreateFile) -> int:
    """
    Save the file information to the database and return the new file ID.
    """
    with get_db() as conn:
        try:
            # Insert the file into the database and get the ID using RETURNING
            result = conn.execute("""
                INSERT INTO files (file_path)
                VALUES (?)
                RETURNING id
            """, [file.file_path]).fetchone()
            return result[0]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file to database: {str(e)}"
            )
        

async def save_uploaded_file(file: UploadFile, user_id: UUID) -> File:
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
    
    file = CreateFile(
        file_path=str(file_path),
    )

    # Save file information to the database
    file_id = await save_file_db(file)
        
    return file_id, file


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


async def get_file_data(file_path: str, limit: int = 20, offset: int = 0) -> tuple[list, int]:
    """
    Read a portion of the CSV file data.
    Returns a tuple of (data_rows, total_rows).
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Get the requested portion
        data = df.iloc[offset:offset + limit].to_dict('records')
        
        return {
            "data": data,
            "total_rows": total_rows,
            "loaded_rows": len(data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file data: {str(e)}"
        )


async def search_file_data(file_path: str, search_term: str, limit: int = 20, offset: int = 0):
    """
    Search CSV file data for rows matching the search term.
    Returns matching rows with pagination and total count.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Convert search term to lowercase for case-insensitive search
        search_term = search_term.lower()
        
        # Function to check if any column in a row contains the search term
        def row_matches_search(row):
            return any(
                str(value).lower().find(search_term) != -1
                for value in row
            )
        
        # Apply the search filter
        matching_df = df[df.apply(row_matches_search, axis=1)]
        total_matches = len(matching_df)
        
        # Get the requested portion
        paginated_df = matching_df.iloc[offset:offset + limit]
        data = paginated_df.to_dict('records')
        
        return {
            "data": data,
            "total_rows": total_matches,
            "loaded_rows": len(data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search file data: {str(e)}"
        )
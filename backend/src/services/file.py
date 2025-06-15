from fastapi import UploadFile, HTTPException
from uuid import uuid4, UUID
from pathlib import Path
import os
import asyncio
import pandas as pd
from typing import Tuple
from ..models.file import CreateFile, File
from ..database import get_db
import difflib
from typing import Optional

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


async def get_file_data(file_path: str = None, limit: int = 20, offset: int = 0) -> Optional[File]:
    """
    Read a portion of the CSV file data.
    Returns a File model containing the data.
    """
    if not file_path or not os.path.exists(file_path):
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Get the requested portion
        data = df.iloc[offset:offset + limit].to_dict('records')
        
        print({
            "data": data,
            "total_rows": total_rows,
            "loaded_rows": len(data)
        })

        return File(
            file_path=file_path,
            data=data,
            total_rows=total_rows,
            loaded_rows=len(data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file data: {str(e)}"
        )


async def search_file_data(file_path: str, search_term: str, limit: int = 20, offset: int = 0) -> Optional[File]:
    """
    Search CSV file data for rows matching the search term.
    Returns matching rows with pagination and total count.
    """
    try:
        if not file_path or not os.path.exists(file_path):
            return None
    
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
        
        return File(
            file_path=file_path,
            data=data,
            total_rows=total_matches,
            loaded_rows=len(data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search file data: {str(e)}"
        )


async def process_file_changes(original_file_path: str, column_name: str, new_values: list, 
                             action_id: int, project_id: UUID) -> File:
    """
    Process changes to a file, create a diff file, and store both in the database.
    Returns File model containing the new file data.
    """
    try:
        # Load the original file with float precision preserved
        df_original = pd.read_csv(original_file_path, dtype=str)
        
        # Create copy for new file
        df_new = df_original.copy()
        df_new[column_name] = new_values

        # Generate timestamp for new files
        file_dir = os.path.dirname(original_file_path)
        file_name = os.path.basename(original_file_path)
        base_name, _ = os.path.splitext(file_name)
        
        # Save new file
        df_new.to_csv(original_file_path, index=False)

        # Find next available diff file number
        diff_number = 1
        while True:
            diff_file_path = os.path.join(file_dir, f"{base_name}_diff_{diff_number}.csv")
            if not os.path.exists(diff_file_path):
                break   
            diff_number += 1

        # Create diff DataFrame by comparing original and new values
        diff_rows = []
        for idx in range(len(df_original)):
            old_val = df_original.at[idx, column_name]
            new_val = df_new.at[idx, column_name]
            if old_val != new_val:
                diff_rows.append({
                    f'new_{column_name}': new_val,
                    f'old_{column_name}': old_val
                })

        # Create diff DataFrame and save as CSV
        if diff_rows:
            df_diff = pd.DataFrame(diff_rows)
            df_diff.to_csv(diff_file_path, index=False)

        # Store file information in database
        with get_db() as conn:
            # Save diff file record
            diff_file_result = conn.execute("""
                INSERT INTO files (file_path)
                VALUES (?)
                RETURNING id
            """, [diff_file_path]).fetchone()

            conn.execute("""
                UPDATE actions 
                SET file_id = ?
                WHERE id = ?
            """, [diff_file_result[0], action_id])

        # Return the file data using get_file_data
        return await get_file_data(original_file_path), await get_file_data(diff_file_path)

    except Exception as e:
        print(f"Error processing file changes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file changes: {str(e)}"
        )


async def revert_action(action_id: int) -> Optional[File]:
    """
    Revert changes made by an action using its diff file.
    Restores original values from the diff file, then deletes the diff file
    and updates the action record.
    """
    try:
        # Get the action's diff file path and project file path from the database
        with get_db() as conn:
            action_data = conn.execute("""
                SELECT df.file_path as diff_path, pf.file_path as project_file_path, a.file_column
                FROM actions a
                JOIN projects p ON a.project_id = p.id
                JOIN files pf ON p.file_id = pf.id
                LEFT JOIN files df ON a.file_id = df.id
                WHERE a.id = ?
            """, [action_id]).fetchone()

        if not action_data or not action_data[0]:
            raise HTTPException(
                status_code=404,
                detail="Diff file not found for this action"
            )

        diff_path = action_data[0]
        project_file_path = action_data[1]
        column_name = action_data[2]

        # Read the project and diff files
        df_project = pd.read_csv(project_file_path, dtype=str)
        df_diff = pd.read_csv(diff_path, dtype=str)

        # Get the old values from diff file
        old_column_name = f'old_{column_name}'
        new_column_name = f'new_{column_name}'

        if old_column_name not in df_diff.columns or new_column_name not in df_diff.columns:
            raise HTTPException(
                status_code=400,
                detail="Invalid diff file format"
            )

        # Create a dictionary mapping new values to old values
        revert_map = dict(zip(df_diff[new_column_name], df_diff[old_column_name]))

        # Apply the revert by replacing current values with original values
        df_project[column_name] = df_project[column_name].map(
            lambda x: revert_map.get(str(x), x)
        )

        # Save the reverted project file
        df_project.to_csv(project_file_path, index=False)

        # Delete the diff file
        await delete_file(diff_path)

        # Update the action record to remove the file_id
        with get_db() as conn:
            conn.execute("""
                UPDATE actions 
                SET file_id = NULL
                WHERE id = ?
            """, [action_id])

        # Return the updated file data
        return await get_file_data(project_file_path)

    except Exception as e:
        print(f"Error reverting action: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revert action: {str(e)}"
        )


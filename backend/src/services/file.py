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


async def get_file_data(file_path: str, limit: int = 20, offset: int = 0) -> File:
    """
    Read a portion of the CSV file data.
    Returns a File model containing the data.
    """
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
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        file_dir = os.path.dirname(original_file_path)
        file_name = os.path.basename(original_file_path)
        base_name, ext = os.path.splitext(file_name)
        
        # Create paths for new and diff files
        new_file_path = os.path.join(file_dir, f"{base_name}_{timestamp}{ext}")
        diff_file_path = os.path.join(file_dir, f"{base_name}_{timestamp}_diff.txt")

        # Save new file
        df_new.to_csv(new_file_path, index=False)

        # Create diff using difflib
        with open(new_file_path, 'r', encoding='utf-8') as f_new, \
             open(original_file_path, 'r', encoding='utf-8') as f_orig:
            new_lines = f_new.readlines()
            orig_lines = f_orig.readlines()

        # Create a unified diff
        diff_lines = list(difflib.unified_diff(
            orig_lines, 
            new_lines,
            fromfile=original_file_path,
            tofile=new_file_path,
            lineterm=''
        ))

        # Write the diff out
        with open(diff_file_path, 'w', encoding='utf-8') as f_diff:
            f_diff.write('\n'.join(diff_lines))

        # Store file information in database
        with get_db() as conn:
            # Save new file record
            new_file_result = conn.execute("""
                INSERT INTO files (file_path)
                VALUES (?)
                RETURNING id
            """, [new_file_path]).fetchone()

            # Save diff file record
            diff_file_result = conn.execute("""
                INSERT INTO files (file_path)
                VALUES (?)
                RETURNING id
            """, [diff_file_path]).fetchone()

            # Update action to point to both new file and diff file
            conn.execute("""
                UPDATE projects 
                SET file_id = ?
                WHERE id = ?
            """, [new_file_result[0], project_id])

            conn.execute("""
                UPDATE actions 
                SET file_id = ?
                WHERE id = ?
            """, [diff_file_result[0], action_id])

            conn.execute("""
                DELETE FROM files 
                WHERE file_path = ?
            """, [original_file_path])

        # Delete the original file and its record from the database after successful updates
        os.remove(original_file_path)

        # Return the file data using get_file_data
        return await get_file_data(new_file_path)

    except Exception as e:
        # If anything fails, make sure to clean up any partially created files
        for path in [new_file_path, diff_file_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass  # Ignore cleanup errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file changes: {str(e)}"
        )


# async def revert_file_changes(action_id: int) -> Tuple[str, str]:
#     """
#     Revert changes made by an action using its diff file.
#     Returns tuple of (new_reverted_file_path, new_diff_file_path)
#     """
#     try:
#         # Get the current file and diff file paths
#         with get_db() as conn:
#             result = conn.execute("""
#                 SELECT f.file_path, d.file_path as diff_path
#                 FROM actions a
#                 JOIN files f ON a.file_id = f.id
#                 JOIN files d ON a.diff_file_id = d.id
#                 WHERE a.id = ?
#             """, [action_id]).fetchone()

#             if not result:
#                 raise ValueError("Action, file or diff file not found")

#             current_file_path, diff_file_path = result

#         # Load the current file
#         df_current = pd.read_csv(current_file_path, dtype=str)
        
#         # Load the diff file
#         with open(diff_file_path, 'r') as f:
#             diff_data = json.load(f)

#         # Create a copy for the reverted file
#         df_reverted = df_current.copy()
        
#         # Apply the changes in reverse
#         changes = diff_data['changes']
#         column_name = diff_data['summary']['column_changed']
        
#         # Create a mapping of row index to old value
#         revert_changes = {change['row_index']: change['old_value'] for change in changes}
        
#         # Apply the reverted changes
#         for idx, old_value in revert_changes.items():
#             df_reverted.at[idx, column_name] = old_value

#         # Generate timestamp for new files
#         timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
#         file_dir = os.path.dirname(current_file_path)
#         file_name = os.path.basename(current_file_path)
#         base_name, ext = os.path.splitext(file_name)
        
#         # Create paths for new and diff files
#         reverted_file_path = os.path.join(file_dir, f"{base_name}_reverted_{timestamp}{ext}")
#         new_diff_file_path = os.path.join(file_dir, f"{base_name}_reverted_{timestamp}_diff.json")

#         # Calculate new differences (should be exactly opposite of original changes)
#         new_differences = []
#         for change in changes:
#             new_differences.append({
#                 "row_index": change['row_index'],
#                 "column": column_name,
#                 "old_value": str(df_current.at[change['row_index'], column_name]),  # Current value becomes old
#                 "new_value": change['old_value']  # Original old value becomes new
#             })

#         # Save new diff file
#         with open(new_diff_file_path, 'w') as f:
#             json.dump({
#                 "changes": new_differences,
#                 "summary": {
#                     "total_rows": len(df_reverted),
#                     "changed_rows": len(changes),
#                     "column_changed": column_name,
#                     "timestamp": timestamp,
#                     "is_revert": True,
#                     "reverted_from_diff": diff_file_path
#                 }
#             }, f, indent=2)

#         # Save reverted file
#         df_reverted.to_csv(reverted_file_path, index=False)

#         # Store file information in database
#         with get_db() as conn:
#             # Save reverted file record
#             new_file_result = conn.execute("""
#                 INSERT INTO files (file_path, is_diff)
#                 VALUES (?, ?)
#                 RETURNING id
#             """, [reverted_file_path, False]).fetchone()

#             # Save new diff file record
#             new_diff_result = conn.execute("""
#                 INSERT INTO files (file_path, is_diff, original_file_id)
#                 VALUES (?, ?, ?)
#                 RETURNING id
#             """, [new_diff_file_path, True, new_file_result[0]]).fetchone()

#             # Update action to point to reverted file
#             conn.execute("""
#                 UPDATE actions 
#                 SET file_id = ?,
#                     diff_file_id = ?
#                 WHERE id = ?
#             """, [new_file_result[0], new_diff_result[0], action_id])

#         return reverted_file_path, new_diff_file_path

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to revert file changes: {str(e)}"
#         )
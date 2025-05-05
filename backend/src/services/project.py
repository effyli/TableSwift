from fastapi import UploadFile, HTTPException
import duckdb
import os
from uuid import uuid4, UUID
from datetime import datetime
from pathlib import Path
from ..database import get_db
from ..models.project import Project, ProjectCreate


async def create_project(project_data: ProjectCreate) -> Project:
    """Create a new project in the database."""
    with get_db() as conn:
        try:
            # Generate UUID for new project
            project_id = uuid4()
            created_at = datetime.now()

            # Insert the project into the database
            conn.execute("""
                INSERT INTO projects (id, name, file_path, user_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, [project_id, project_data.name, project_data.file_path, project_data.user_id, created_at])

            # Return the created project
            return Project(
                id=project_id,
                name=project_data.name,
                file_path=project_data.file_path,
                user_id=project_data.user_id,
                created_at=created_at
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create project in database: {str(e)}"
            )
 

async def save_uploaded_file(file: UploadFile, user_id: UUID) -> tuple[str, str]:
    """
    Save the uploaded file to the user's directory and return the file path and name.
    """
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

def get_user_projects(user_id: UUID) -> list[Project]:
    """Get all projects for a specific user."""
    with get_db() as conn:
        try:
            results = conn.execute("""
                SELECT id, name, file_path, user_id, created_at
                FROM projects
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, [user_id]).fetchall()
            
            return [
                Project(
                    id=row[0],
                    name=row[1],
                    file_path=row[2],
                    user_id=row[3],
                    created_at=row[4]
                )
                for row in results
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch projects: {str(e)}"
            )
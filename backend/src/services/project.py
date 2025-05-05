from fastapi import HTTPException
from uuid import uuid4, UUID
from datetime import datetime
from ..database import get_db
from ..models.project import ProjectBase, ProjectCreate, Project


async def create_project(project_data: ProjectCreate) -> ProjectBase:
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
            return ProjectBase(
                id=project_id,
                name=project_data.name,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create project in database: {str(e)}"
            )

def get_user_projects(user_id: UUID) -> list[ProjectBase]:
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
                ProjectBase(
                    id=row[0],
                    name=row[1],
                )
                for row in results
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch projects: {str(e)}"
            )
        
async def get_user_project(project_id: UUID, user_id: UUID) -> Project:
    """Get a specific project by ID for a specific user."""
    with get_db() as conn:
        try:
            result = conn.execute("""
                SELECT id, name, file_path, user_id, created_at
                FROM projects
                WHERE id = ? AND user_id = ?
            """, [project_id, user_id]).fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )
            
            return Project(
                id=result[0],
                name=result[1],
                file_path=result[2],
                user_id=result[3],
                created_at=result[4],
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch project: {str(e)}"
            )
        
def delete_project(project_id: UUID, user_id: UUID) -> bool:
    with get_db() as conn:
        try:
            result = conn.execute("""
                DELETE FROM projects
                WHERE id = ? AND user_id = ?
            """, [project_id, user_id])
            return result.rowcount > 0
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete project: {str(e)}"
            )
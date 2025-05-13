from fastapi import HTTPException
from uuid import uuid4, UUID
from ..database import get_db
from ..models.project import ProjectBase, ProjectCreate, Project
from ..models.file import File
from .action import delete_action


async def create_project(project_data: ProjectCreate) -> ProjectBase:
    """Create a new project in the database."""
    with get_db() as conn:
        try:
            # Generate UUID for new project
            project_id = uuid4()

            # Insert the project into the database
            conn.execute("""
                INSERT INTO projects (id, name, file_id, user_id)
                VALUES (?, ?, ?, ?)
            """, [project_id, project_data.name, project_data.file_id, project_data.user_id])

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
                SELECT id, name
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
                SELECT p.id, p.name, p.created_at, f.file_path
                FROM projects p
                JOIN files f ON p.file_id = f.id
                WHERE p.id = ? AND p.user_id = ?
            """, [project_id, user_id]).fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )
            
            return Project(
                id=result[0],
                name=result[1],
                created_at=result[2],
                file=File(file_path=result[3])
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch project: {str(e)}"
            )
        
def delete_project(project_id: UUID, user_id: UUID) -> bool:
    with get_db() as conn:
        try:
            file_result = conn.execute("""
                DELETE FROM files
                WHERE id = (
                    SELECT file_id
                    FROM projects
                    WHERE id = ? AND user_id = ?
                )
            """, [project_id, user_id])
            if file_result.rowcount == 0:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Delete all actions
            action_ids = conn.execute("""
                SELECT id FROM actions
                WHERE project_id = ?
            """, [project_id]).fetchall()
            action_ids = [action_id[0] for action_id in action_ids]

            for action_id in action_ids:
                delete_action(action_id)

            # Then delete the project
            project_result = conn.execute("""
                DELETE FROM projects
                WHERE id = ? AND user_id = ?
            """, [project_id, user_id])
            if project_result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")

            return True

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete project: {str(e)}"
            )

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ..dependencies import validate_token
from ..services.project import create_project, get_user_projects, get_user_project, delete_project
from ..services.file import save_uploaded_file, delete_file
from ..dependencies.csrf import validate_csrf_token
from ..models.project import ProjectBase, ProjectCreate, Project
from ..models.user import TokenData
from typing import List
import traceback
from uuid import UUID

router = APIRouter(
    prefix="/project",
    tags=["project"]
)

@router.post("/", response_model=ProjectBase, dependencies=[Depends(validate_csrf_token)])
async def generate_project(
    file: UploadFile = File(...),
    token_data: TokenData = Depends(validate_token)
):
    """Create a new project with an uploaded file."""
    try:
        # Validate file exists and has filename
        if not file or not hasattr(file, 'filename') or not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded or invalid file"
            )

        # Validate file type (only allow CSV)
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )

        # Validate file size (10MB limit)
        file_size = 0
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        content = await file.read(MAX_FILE_SIZE + 1)
        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 10MB"
            )

        # Save the file
        try:
            file_path, file_name = await save_uploaded_file(file, token_data.user_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Create project
        project_data = ProjectCreate(
            name=file_name,
            file_path=file_path,
            user_id=token_data.user_id
        )
        
        # Create the project in the database
        project = await create_project(project_data)
        return project
        
    except Exception as e:
        print(f"Error in create_project: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to create project"
        )


@router.get("/", response_model=List[ProjectBase])
async def list_projects(token_data: TokenData = Depends(validate_token)):
    """Get all projects for the current user."""
    try:
        return get_user_projects(token_data.user_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in list_projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch projects"
        )
    
@router.delete("/{project_id}", response_model=dict, dependencies=[Depends(validate_csrf_token)])
async def delete_project_endpoint(project_id: UUID, token_data: TokenData = Depends(validate_token)):
    """Delete a specific project and its associated files."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        # First, get the project to verify ownership and get file path
        project = await get_user_project(project_id, token_data.user_id)
        
        try:
            # First try to delete the file
            await delete_file(project.file_path)
            
            # If file deletion successful, delete from database
            delete_project(project_id, token_data.user_id)
            
            return {"status": "success", "message": "Project and associated files deleted successfully"}
            
        except Exception as e:
            # If anything fails during deletion, raise an error
            print(f"Error during project deletion: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail="Failed to delete project or its files. No changes were made."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_project_endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
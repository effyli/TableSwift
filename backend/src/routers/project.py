from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from ..dependencies import validate_token
from ..services.project import create_project, save_uploaded_file, get_user_projects
from ..dependencies.csrf import validate_csrf_token
from ..models.project import ProjectCreate, Project
from ..models.user import TokenData
from typing import List, Annotated
import traceback

router = APIRouter(
    prefix="/project",
    tags=["project"]
)

@router.post("/", dependencies=[Depends(validate_csrf_token)])
async def generate_project(
    file: UploadFile = File(...),
    token_data: TokenData = Depends(validate_token)
):
    """Create a new project with an uploaded file."""
    try:
        # Validate file type (only allow CSV)
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
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

@router.get("/", response_model=List[Project])
async def list_projects(token_data: TokenData = Depends(validate_token)):
    """Get all projects for the current user."""
    try:
        if not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User ID is required"
            )
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
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from ..dependencies import validate_token
from ..services.project import create_project, get_user_projects, get_user_project, delete_project
from ..services.file import save_uploaded_file, delete_file, get_file_data, search_file_data
from ..dependencies.csrf import validate_csrf_token
from ..models.project import ProjectBase, ProjectCreate, Project
from ..models.user import TokenData
from typing import List
import traceback
from uuid import UUID
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/project",
    tags=["project"]
)

LIMIT = 20

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
            file_id, file_obj = await save_uploaded_file(file, token_data.user_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Create project
        project_data = ProjectCreate(
            name=file.filename,
            file_id=file_id,
            file=file_obj,
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
            print(f"Attempting to delete file at {project.file.file_path}")
            await delete_file(project.file.file_path)
            
            # Clear cache for the project
            await FastAPICache.clear(namespace="{project_id}")
            
            # If file deletion successful, delete from database
            delete_project(project.id, token_data.user_id)

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

@router.get("/{project_id}", response_model=Project)
async def get_project_details(project_id: UUID, token_data: TokenData = Depends(validate_token)):
    """Get detailed project information including file data."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        # Get project with file info
        project = await get_user_project(project_id, token_data.user_id)
        
        # Get file data with pagination
        try:
            file_data = await get_file_data(project.file.file_path)
            project.file.data = file_data["data"]
            project.file.total_rows = file_data["total_rows"]
            project.file.loaded_rows = file_data["loaded_rows"]
        except Exception as e:
            print(f"Error reading file data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to read file data"
            )
        
        return project
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_project_details: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch project details"
        )

@router.get("/{project_id}/data", response_model=dict)
@cache(namespace="{project_id}", expire=60)
async def get_project_data(
    project_id: UUID,
    offset: int,
    limit: int = LIMIT,
    token_data: TokenData = Depends(validate_token)
):
    """Get paginated project file data."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        # Get project to verify ownership and get file path
        project = await get_user_project(project_id, token_data.user_id)
        
        # If not in cache, get file data with pagination
        try:
            file_data = await get_file_data(project.file.file_path, limit=limit, offset=offset)
            return file_data
        except Exception as e:
            print(f"Error reading file data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to read file data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_project_data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch project data"
        )

@router.get("/{project_id}/search")
@cache(namespace="{project_id}", expire=60)
async def search_project_data(
    project_id: UUID,
    query: str = Query(..., description="Search term to filter rows"),
    offset: int = Query(0, description="Number of rows to skip"),
    limit: int = Query(LIMIT, description="Number of rows to return"),
    token_data: TokenData = Depends(validate_token)
):
    """Search project data for rows matching the query term."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        # Get project to verify ownership and get file path
        project = await get_user_project(project_id, token_data.user_id)
        
        # If not in cache, perform the search
        try:
            search_results = await search_file_data(
                project.file.file_path,
                query,
                limit=limit,
                offset=offset
            )
            return search_results
            
        except Exception as e:
            print(f"Error searching file data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to search file data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in search_project_data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to search project data"
        )
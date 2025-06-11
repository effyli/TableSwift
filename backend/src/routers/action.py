from fastapi import APIRouter, HTTPException, Depends, status
from ..models.action import Action, ActionCreate, ActionBase
from ..models.user import TokenData
from ..services.action import create_action, get_action, update_action, delete_action, generate_action_labels, update_labels, generate_action_code, update_code, execute_code, check_action_ownership, check_label_ownership, check_code_ownership
from ..services.file import get_file_data, search_file_data
from ..dependencies import validate_token
from ..dependencies.csrf import validate_csrf_token
import traceback
from ..models.labels import Labels
from ..models.description import Description
from ..models.code import Code
from ..models.file import File

router = APIRouter(
    prefix="/action",
    tags=["action"],
    dependencies=[Depends(validate_csrf_token)]
)

LIMIT = 20

@router.post("", response_model=ActionBase, dependencies=[Depends(validate_csrf_token)]) 
async def create_new_action(action_create: ActionCreate, _: TokenData = Depends(validate_token)):
    """Create a new action."""
    try:
        return create_action(action_create)
    except Exception as e:
        print(f"Error in list_projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{action_id}", response_model=Action)
async def get_single_action(action_id: int, token_data: TokenData = Depends(validate_token)):
    """Get a single action by ID."""
    try:
        if not check_action_ownership(action_id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        return await get_action(action_id)
    except ValueError as e:
        print(f"Error in list_projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{action_id}", response_model=Action, dependencies=[Depends(validate_csrf_token)])
async def update_single_action(action_id: int, action: Action, token_data: TokenData = Depends(validate_token)):
    try:
        if not check_action_ownership(action_id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        return update_action(action_id, action)
    except ValueError as e:
        # For known validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error updating action: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update action"
        )
    
@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(validate_csrf_token)])
async def delete_single_action(action_id: int, token_data: TokenData = Depends(validate_token)):
    try:
        if not check_action_ownership(action_id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        delete_action(action_id)
        return {"message": "Action deleted successfully"}
    except ValueError as e:
        print(f"Error in delete_single_action: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error in delete_single_action: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete action"
        )
    
@router.post("/generate_labels", response_model=Description, dependencies=[Depends(validate_csrf_token)])
async def generate_labels(action: Action, token_data: TokenData = Depends(validate_token)):
    """Generate labels for the action."""
    try:
        if not check_action_ownership(action.id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        # Assuming you have a function to generate labels
        return await generate_action_labels(action, token_data.user_id)
    except Exception as e:
        print(f"Error in generate_labels: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate labels"
        )
    
@router.post("/save_labels", dependencies=[Depends(validate_csrf_token)])
async def save_labels(labels: Labels, token_data: TokenData = Depends(validate_token)):
    """Save labels for the action."""
    try:
        if not check_label_ownership(labels.id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this label"
            )

        # Assuming you have a function to save labels
        update_labels(labels)
        return {"message": "Labels saved successfully"}
    except Exception as e:
        print(f"Error in save_labels: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save labels"
        )


@router.post("/generate_code", response_model=Code, dependencies=[Depends(validate_csrf_token)])
async def generate_labels(action: Action, token_data: TokenData = Depends(validate_token)):
    """Generate labels for the action."""
    try:
        if not check_action_ownership(action.id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        return generate_action_code(action)
    except Exception as e:
        print(f"Error in generate_labels: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate labels"
        )
    

@router.post("/save_code", dependencies=[Depends(validate_csrf_token)])
async def save_code(code: Code, token_data: TokenData = Depends(validate_token)):
    """Save code for the action."""
    try:
        if not check_code_ownership(code.id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this code"
            )
        
        # Assuming you have a function to save labels
        update_code(code)
        return {"message": "Code saved successfully"}
    except Exception as e:
        print(f"Error in save_code: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save code"
        )
    
@router.post("/execute_code", dependencies=[Depends(validate_csrf_token)], response_model=File)
async def execute_code_endpoint(action: Action, token_data: TokenData = Depends(validate_token)):
    """Execute code for the action."""
    try:
        if not check_action_ownership(action.id, token_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )
        
        return await execute_code(action, token_data.user_id)
    except Exception as e:
        print(f"Error in execute_code: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute code"
        )

@router.get("/{action_id}/affected_rows", response_model=File)
async def get_action_data(
    action_id: int,
    offset: int,
    limit: int = LIMIT,
    token_data: TokenData = Depends(validate_token)
):
    """Get paginated action file data."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        action = await get_action(action_id)
        if not action or check_action_ownership(action_id, token_data.user_id) is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )

        try:
            file_data = await get_file_data(action.file.file_path, limit=limit, offset=offset)
            return file_data
        except Exception as e:
            print(f"Error reading file data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read file data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_project_data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project data"
        )

@router.get("/{action_id}/search", response_model=File)
async def get_action_data(
    action_id: int,
    query: str,
    offset: int,
    limit: int = LIMIT,
    token_data: TokenData = Depends(validate_token)
):
    """Get paginated action file data."""
    try:
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=401,
                detail="User authentication required"
            )

        action = await get_action(action_id)
        if not action or check_action_ownership(action_id, token_data.user_id) is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this action"
            )

        try:
            search_results = await search_file_data(
                action.file.file_path,
                query,
                limit=limit,
                offset=offset
            )
            return search_results
        except Exception as e:
            print(f"Error reading file data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read file data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_project_data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project data"
        )
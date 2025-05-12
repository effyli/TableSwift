from fastapi import APIRouter, HTTPException, Depends, status
from ..models.action import Action, ActionCreate, ActionBase
from ..models.user import TokenData
from ..services.action import create_action, get_action, update_action, delete_action
from ..dependencies import validate_token
from ..dependencies.csrf import validate_csrf_token
import traceback

router = APIRouter(
    prefix="/action",
    tags=["action"],
    dependencies=[Depends(validate_csrf_token)]
)

@router.post("", response_model=ActionBase) 
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
async def get_single_action(action_id: int, _: TokenData = Depends(validate_token)):
    """Get a single action by ID."""
    try:
        return get_action(action_id)
    except ValueError as e:
        print(f"Error in list_projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{action_id}", response_model=Action)
async def update_single_action(action_id: int, action: Action, _: TokenData = Depends(validate_token)):
    try:
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
    
@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_action(action_id: int, _: TokenData = Depends(validate_token)):
    try:
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
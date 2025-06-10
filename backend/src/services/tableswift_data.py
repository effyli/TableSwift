from fastapi import HTTPException
from ..database import get_db
from uuid import UUID
from typing import Optional
import pandas as pd


def get_project_file_path(project_id: UUID, user_id: UUID) -> str:
    """Get a project's file path by its ID."""
    with get_db() as conn:
        result = conn.execute("""
            SELECT p.id, p.name, p.created_at, f.file_path
            FROM projects p
            JOIN files f ON p.file_id = f.id
            WHERE p.id = ? AND p.user_id = ?
        """, [project_id, user_id]).fetchone()
        
        if not result:
            raise ValueError("Project not found")

        return result[3]
    

async def get_file_data_tableswift(project_id: UUID, user_id: UUID, column: Optional[str]) -> list[dict[str, str]]:
    """
    Read a portion of the CSV file data.
    Returns a tuple of (data_rows, total_rows).
    """
    try:
        file_path = get_project_file_path(project_id, user_id)

        # Read the CSV file
        df = pd.read_csv(file_path)
        
        if column:
            # Check if column exists
            if column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{column}' does not exist in the file."
                )
            
            result = [{"Input": str(value), "Output": ""} for value in df[column]]
        else:
            # Map entire rows to Input/Output format
            # TODO format correctly
            result = [{"Input": str(row), "Output": ""} for _, row in df.iterrows()]
            
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file data: {str(e)}"
        )


def format_data_tableswift(labels_data, column):
    # Transform the labels into the expected format
    formatted_labels = []
    for label_pair in labels_data:
        formatted_labels.append({
            "Input": label_pair[0][column],
            "Output": label_pair[1]["Label"]
        })
    return formatted_labels
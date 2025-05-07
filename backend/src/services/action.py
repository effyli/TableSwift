from datetime import datetime
from ..models.action import ActionBase, Action, ActionCreate, ActionUpdate
from ..models.operation import Operation
from ..database import get_db
from uuid import UUID

def create_action(action_create: ActionCreate) -> ActionBase:
    """Create a new action in the database."""
    with get_db() as conn:
        result = conn.execute("""
            INSERT INTO actions (project_id, datetime)
            VALUES (?, ?)
            RETURNING id, project_id, datetime
        """, [str(action_create.project_id), datetime.now()]).fetchone()
        
        return ActionBase(
            id=result[0],
            project_id=result[1],
            datetime=result[2]
        )

def get_action(action_id: int) -> Action:
    """Get an action by its ID."""
    with get_db() as conn:
        result = conn.execute("""
            SELECT 
                a.id, 
                a.project_id, 
                a.datetime, 
                a.operation_id,
                o.name AS operation_name,
                a.file_column, 
                a.description
            FROM actions a
            LEFT JOIN operations o ON a.operation_id = o.id
            WHERE a.id = ?
        """, [action_id]).fetchone()
        
        if not result:
            raise ValueError("Action not found")
        
        return Action(
            id=result[0],
            project_id=result[1],
            datetime=result[2],
            operation=Operation(id=result[3], name=result[4]) if result[3] else None,
            file_column=result[5],
            description=result[6]
        )

async def get_project_actions(project_id: UUID) -> list[ActionBase]:
    """Get all actions for a project."""
    with get_db() as conn:
        results = conn.execute("""
            SELECT 
                a.id, 
                a.project_id, 
                a.datetime, 
                a.operation_id,
                o.name AS operation_name,
                a.file_column
            FROM actions a
            LEFT JOIN operations o ON a.operation_id = o.id
            WHERE a.project_id = ?
            ORDER BY a.datetime DESC
        """, [str(project_id)]).fetchall()
        
        return [
            ActionBase(
                id=row[0],
                project_id=row[1],
                datetime=row[2],
                operation=Operation(id=row[3], name=row[4]) if row[3] else None,
                file_column=row[5]
            )
            for row in results
        ]

def update_action(action_id: int, action_update: ActionUpdate) -> Action:
    """Update an action with new data."""
    with get_db() as conn:
        # First get the project id and file path for this action
        action = conn.execute("""
            SELECT a.project_id, f.file_path
            FROM actions a
            JOIN projects p ON a.project_id = p.id
            JOIN files f ON p.file_id = f.id
            WHERE a.id = ?
        """, [action_id]).fetchone()

        if not action:
            raise ValueError("Action not found")

        # Read the first row of the CSV file to get column headers
        import pandas as pd
        df = pd.read_csv(action[1], nrows=1)
        columns = df.columns.tolist()

        # Check if the specified column exists
        if action_update.file_column and action_update.file_column not in columns:
            raise ValueError(f"Column '{action_update.file_column}' not found in file. Available columns: {', '.join(columns)}")

        # If validation passes, update the action
        conn.execute("""
            UPDATE actions
            SET operation_id = ?, file_column = ?, description = ?
            WHERE id = ?
        """, [
            action_update.operation_id,
            action_update.file_column,
            action_update.description,
            action_id
        ])
        
        return get_action(action_id)
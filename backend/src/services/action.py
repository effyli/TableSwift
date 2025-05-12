from datetime import datetime
from ..models.action import ActionBase, Action, ActionCreate
from ..models.operation import Operation
from ..database import get_db
from uuid import UUID
import pandas as pd
import json
from ..models.labels import Labels


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
        # First get the action details
        action_result = conn.execute("""
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
        
        if not action_result:
            raise ValueError("Action not found")

        # Get all labels for this action
        labels_result = conn.execute("""
            SELECT id, json, version
            FROM labels 
            WHERE action_id = ?
            ORDER BY version
        """, [action_id]).fetchall()

        labels = []
        for label in labels_result:
            # Get all codes for this label
            codes_result = conn.execute("""
                SELECT id, code, version
                FROM codes 
                WHERE label_id = ?
                ORDER BY version
            """, [label[0]]).fetchall()

            codes = [
                {
                    'id': code[0],
                    'code': code[1],
                    'version': code[2]
                }
                for code in codes_result
            ]

            labels.append({
                'id': label[0],
                'json': label[1],
                'version': label[2],
                'codes': codes
            })
        
        return Action(
            id=action_result[0],
            project_id=action_result[1],
            datetime=action_result[2],
            operation=Operation(id=action_result[3], name=action_result[4]) if action_result[3] else None,
            file_column=action_result[5],
            description=action_result[6],
            labels=labels
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
    

def check_column_exists(action_id: int, column_name: str) -> bool:
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
        df = pd.read_csv(action[1], nrows=1)
        columns = df.columns.tolist()

        # Check if the specified column exists
        if column_name and column_name not in columns:
            raise ValueError(f"Column '{column_name}' not found in file. Available columns: {', '.join(columns)}")


def update_action(action_id: int, action: Action) -> Action:
    """Update an action with new data."""
    with get_db() as conn:
        # Check if the action exists
        try:
            check_column_exists(action_id, action.file_column)
        except ValueError as e:
            # If the column does not exist, raise an error
            raise ValueError(f"Validation error: {str(e)}")

        # If validation passes, update the action with current datetime
        conn.execute("""
            UPDATE actions
            SET operation_id = ?, 
                file_column = ?, 
                description = ?, 
                datetime = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [
            action.operation.id,
            action.file_column,
            action.description,
            action_id
        ])
        
        return get_action(action_id)
    
def delete_action(action_id: int) -> None:
    """Delete an action and its related data by its ID."""
    with get_db() as conn:
        # Check if the action exists and is reverted
        action = conn.execute("""
            SELECT file_id FROM actions WHERE id = ?
        """, [action_id]).fetchone()
        
        if not action:
            raise ValueError("Action not found")
        if action[0] is not None:
            raise ValueError("Action cannot be deleted because it is not reverted yet")

        # First delete codes linked to this action's labels
        conn.execute("""
            DELETE FROM codes 
            WHERE label_id IN (
                SELECT id FROM labels WHERE action_id = ?
            )
        """, [action_id])

        # Then delete the labels
        conn.execute("""
            DELETE FROM labels WHERE action_id = ?
        """, [action_id])

        # Finally delete the action itself
        conn.execute("""
            DELETE FROM actions WHERE id = ?
        """, [action_id])
        return None
    

def generate_action_labels(action: Action) -> Labels:
    """Generate labels for an action."""
    
    # TODO Send the operation, column, and description to the TableSwift framework to generate labels
    # This is a placeholder for the actual implementation
    input = {
        "function": action.operation.name,
        "column": action.file_column,
        "description": action.description,
    }

    output = [
        [{"Person": "John Doe"}, {"Label": "john doe"}],
        [{"Person": "Jane Smith"}, {"Label": "jane smith"}],
        [{"Person": "Bob Johnson"}, {"Label": "bob johnson"}],
        [{"Person": "Mary Williams"}, {"Label": "mary williams"}],
        [{"Person": "James Brown",}, {"Label": "james brown"}]
    ]

    with get_db() as conn:
        result = conn.execute("""
            INSERT INTO labels (json, version, action_id)
            VALUES (?, 
               COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 
                    FROM labels 
                    WHERE action_id = ?), 1),
               ?)
            RETURNING id, version
        """, [json.dumps(output), action.id, action.id]).fetchone()

    return Labels(
        id=result[0],
        json=json.dumps(output),
        version=result[1],
        codes=[]
    )


    # output = [
    #     [
    #         {
    #             "Person": "John Doe",
    #             "Age": 30.0,
    #         },
    #         {
    #             "Person": "john doe",
    #             "Age": 30,
    #         },
    #     ],
    #     [
    #         {
    #             "Person": "Jane Smith",
    #             "Age": 25.0,
    #         }, 
    #         {
    #             "Person": "jane smith",
    #             "Age": 25,
    #         }
    #     ],
    #     [
    #         {
    #             "Person": "John Doe",
    #             "Age": 30.0,
    #         },
    #         {
    #             "Person": "john doe",
    #             "Age": 30,
    #         },
    #     ],
    #     [
    #         {
    #             "Person": "Jane Smith",
    #             "Age": 25.0,
    #         }, 
    #         {
    #             "Person": "jane smith",
    #             "Age": 25,
    #         }
    #     ],
    # ]
    # output = [
    #     [{
    #         "Person": "John Doe",
    #         "Age": 30,
    #     }, "john doe"],
    #     [{
    #         "Person": "Jane Smith",
    #         "Age": 25,
    #     }, "jane smith"],
    #     [{
    #         "Person": "Bob Johnson",
    #         "Age": 40,
    #     }, "bob johnson"],
    #     [{
    #         "Person": "Mary Williams",
    #         "Age": 35,
    #     }, "mary williams"],
    #     [{
    #         "Person": "James Brown",
    #         "Age": 50,
    #     }, "james brown"]
    # ]
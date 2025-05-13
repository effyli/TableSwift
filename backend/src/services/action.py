from datetime import datetime
from typing import List
from ..models.code import Code
from ..models.action import ActionBase, Action, ActionCreate
from ..models.operation import Operation
from ..models.labels import Labels
from ..models.description import Description
from ..database import get_db
from uuid import UUID
import pandas as pd
import json


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
                a.file_column 
            FROM actions a
            LEFT JOIN operations o ON a.operation_id = o.id
            WHERE a.id = ?
        """, [action_id]).fetchone()
        
        if not action_result:
            raise ValueError("Action not found")

        # Get all descriptions with their labels for this action
        descriptions_result = conn.execute("""
            SELECT 
            d.id, 
            d.description, 
            d.version
            FROM description d
            WHERE d.action_id = ?
            ORDER BY d.version
        """, [action_id]).fetchall()

            
        descriptions = []
        for desc in descriptions_result:
            # Get all labels for this description
            labels_result = conn.execute("""
                SELECT id, json, version
                FROM labels
                WHERE description_id = ?
                ORDER BY version
            """, [desc[0]]).fetchall()

            labels = []
            for label in labels_result:
                # Get all codes for this description
                codes_result = conn.execute("""
                    SELECT id, code, version
                    FROM codes 
                    WHERE label_id = ?
                    ORDER BY version
                """, [label[0]]).fetchall()

                codes = [Code(
                    id=code[0],
                    code=code[1],
                    version=code[2]
                ) for code in codes_result]

                labels.append(Labels(
                    id=label[0],
                    json=label[1],
                    version=label[2],
                    codes=codes
                ))

            descriptions.append(Description(
                id=desc[0],
                description=desc[1],
                version=desc[2],
                labels=labels
            ))

        return Action(
            id=action_result[0],
            project_id=action_result[1],
            datetime=action_result[2],
            operation=Operation(id=action_result[3], name=action_result[4]) if action_result[3] else None,
            file_column=action_result[5],
            active_description=0,
            descriptions=descriptions
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


def save_codes() -> None:
    """Save codes to the database."""
    pass


def save_labels(desc_id: int, labels: List[Labels]) -> None:
    with get_db() as conn:
        for label in labels:
            # Check if the label exists
            existing_labels = conn.execute("""
                SELECT id FROM labels WHERE id = ?
            """, [label.id]).fetchone()

            if not existing_labels:
                # If it doesn't exist, create a new one
                conn.execute("""
                    INSERT INTO labels (json, version, description_id)
                    VALUES (?, COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 FROM labels WHERE description_id = ?), 1), ?)
                """, [
                    json.dumps(label.json),
                    desc_id,  # For the version subquery
                    desc_id
                ])
            else:
                # If it exists, update it
                conn.execute("""
                    UPDATE labels SET 
                        json = ?,
                    WHERE id = ?
                """, [
                    json.dumps(label.json),
                    label.id
                ])
                
                # TODO save codes
                if label.codes:
                    save_codes(label.id, label.codes)


def save_descriptions(action_id: int, descriptions: list[Description]) -> None:
    with get_db() as conn:
        for desc in descriptions:
            # Check if the description exists
            existing_desc = conn.execute("""
                SELECT id FROM description WHERE id = ?
            """, [desc.id]).fetchone()

            if not existing_desc:
                # If it doesn't exist, create a new one
                conn.execute("""
                    INSERT INTO description (description, version, action_id)
                    VALUES (?, 
                        COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 
                            FROM description 
                            WHERE action_id = ?), 1),
                        ?)
                """, [
                    desc.description,
                    action_id,  # For the version subquery
                    action_id
                ])
            else:
                # If it exists, update it
                conn.execute("""
                    UPDATE description SET 
                        description = ?,
                    WHERE id = ?
                """, [
                    desc.description,
                    desc.id
                ])

                if desc.labels:
                    save_labels(desc.id, desc.labels)


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
                datetime = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [
            action.operation.id,
            action.file_column,
            action_id
        ])

        save_descriptions(action_id, action.descriptions)

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
                SELECT id FROM labels WHERE description_id IN (
                    SELECT id FROM description WHERE action_id = ?
                )
            )
        """, [action_id])

        # Then delete the labels
        conn.execute("""
            DELETE FROM labels WHERE description_id IN (
                SELECT id FROM description WHERE action_id = ?
            )
        """, [action_id])

        # Delete the descriptions
        conn.execute("""
            DELETE FROM description WHERE action_id = ?
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
        "description": action.descriptions[action.active_description].description,
    }

    output = [
        [{"Person": "John Doe"}, {"Label": "john doe"}],
        [{"Person": "Jane Smith"}, {"Label": "jane smith"}],
        [{"Person": "Bob Johnson"}, {"Label": "bob johnson"}],
        [{"Person": "Mary Williams"}, {"Label": "mary williams"}],
        [{"Person": "James Brown",}, {"Label": "james brown"}]
    ]

    saved_action = update_action(action.id, action)

    with get_db() as conn:
        # First get the next version number
        version_result = conn.execute("""
            SELECT COALESCE(MAX(version) + 1, 1)
            FROM labels
            WHERE description_id = ?
        """, [saved_action.descriptions[action.active_description].id]).fetchone()
        
        next_version = version_result[0]

        # Then do the insert
        result = conn.execute("""
            INSERT INTO labels (json, description_id, version)
            VALUES (?, ?, ?)
            RETURNING id
        """, [
            json.dumps(output),
            saved_action.descriptions[action.active_description].id,
            next_version
        ]).fetchone()

    return Labels(
        id=result[0],
        json=json.dumps(output),
        version=next_version,
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
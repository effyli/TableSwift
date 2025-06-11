from datetime import datetime
from typing import List
from ..models.code import Code
from ..models.action import ActionBase, Action, ActionCreate
from ..models.operation import Operation
from ..models.labels import Labels
from ..models.description import Description
from ..models.file import File
from .tableswift_data import get_file_data_tableswift, format_data_tableswift
from ..database import get_db
from .file import process_file_changes, get_file_data
from uuid import UUID
import pandas as pd
import json
import tableswift as ts
from ..config import get_settings


settings = get_settings()

# TODO store the operations correctly
OPERATIONS = [
    "data_transformation",
    "error_detection_spelling",
    "data_imputation",
    "entity_matching"
]


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
    

async def get_action(action_id: int) -> Action:
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
                f.file_path
            FROM actions a
            LEFT JOIN operations o ON a.operation_id = o.id
            LEFT JOIN files f ON a.file_id = f.id
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
                    SELECT id, code, router_code, version
                    FROM codes 
                    WHERE label_id = ?
                    ORDER BY version
                """, [label[0]]).fetchall()

                codes = [Code(
                    id=code[0],
                    code=code[1],
                    router_code=code[2],
                    version=code[3]
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
            active_description=len(descriptions) - 1,
            active_labels=len(descriptions[-1].labels) - 1 if descriptions else 0,
            active_code=len(descriptions[-1].labels[-1].codes) - 1 if descriptions and descriptions[-1].labels else 0,
            descriptions=descriptions,
            file=await get_file_data(action_result[6])
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


def save_code(label_id: int, code: Code) -> Code:
    """Save a code to the database."""
    with get_db() as conn:
        # Check if the code exists
        existing_code = conn.execute("""
            SELECT id FROM codes WHERE id = ?
        """, [code.id]).fetchone()

        if not existing_code:
            # If it doesn't exist, create a new one
            new_code = conn.execute("""
                INSERT INTO codes (code, router_code, label_id, version)
                VALUES (?, ?, ?, COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 FROM codes WHERE label_id = ?), 1))
                RETURNING id, code, router_code, version
            """, [
                code.code,
                code.router_code,
                label_id,
                label_id  # For the version subquery
            ]).fetchone()

            return Code(
                id=new_code[0],
                code=new_code[1],
                router_code=new_code[2],
                version=new_code[2]
            )
        else:
            # If it exists, update it
            resultCode = conn.execute("""
                UPDATE codes SET 
                    code = ?
                WHERE id = ?
                RETURNING id, code, router_code, version
            """, [
                code.code,
                code.id
            ]).fetchone()

            return Code(
                id=resultCode[0],
                code=resultCode[1],
                router_code=resultCode[2],
                version=resultCode[3]
            )


def save_codes(label_id: int, codes: list[Code]) -> list[int]:
    """Save codes to the database."""
    return [save_code(label_id, code) for code in codes]


def save_label(desc_id: int, label: Labels) -> None:
    with get_db() as conn:
        # Check if the label exists
        existing_labels = conn.execute("""
            SELECT id FROM labels WHERE id = ?
        """, [label.id]).fetchone()

        if not existing_labels:
            # If it doesn't exist, create a new one
            new_label = conn.execute("""
                INSERT INTO labels (json, version, description_id)
                VALUES (?, COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 FROM labels WHERE description_id = ?), 1), ?)
                RETURNING id, json, version
            """, [
                json.dumps(label.json),
                desc_id,  # For the version subquery
                desc_id
            ]).fetchone()

            return Labels(
                id=new_label[0],
                json=new_label[1],
                version=new_label[2],
                codes=[]
            )
        else:
            # If it exists, update it
            resultLabel = conn.execute("""
                UPDATE labels SET 
                    json = ?
                WHERE id = ?
                RETURNING id, json, version
            """, [
                json.dumps(label.json),
                label.id
            ]).fetchone()

            return Labels(
                id=resultLabel[0],
                json=resultLabel[1],
                version=resultLabel[2],
                codes=save_codes(resultLabel[0], label.codes) if label.codes else []
            )


def save_labels(desc_id: int, labels: List[Labels]) -> None:
    return [save_label(desc_id, label) for label in labels if label.json]


def save_description(action_id: int, description: Description) -> Description:
    with get_db() as conn:
        # Check if the description exists
        existing_desc = conn.execute("""
            SELECT id FROM description WHERE id = ?
        """, [description.id]).fetchone()

        if not existing_desc:
            # If it doesn't exist, create a new one
            result = conn.execute("""
                INSERT INTO description (description, version, action_id)
                VALUES (?, COALESCE((SELECT CAST(MAX(version) AS INTEGER) + 1 FROM description WHERE action_id = ?), 1), ?)
                RETURNING id, description, version
            """, [
                description.description,
                action_id,  # For the version subquery
                action_id
            ]).fetchone()
            
            new_desc = Description(
                id=result[0],
                description=result[1],
                version=result[2],
                labels=[]
            )
            return new_desc
        else:
            # If it exists, update it
            desc = conn.execute("""
                UPDATE description SET 
                    description = ?
                WHERE id = ?
                RETURNING id, description, version
            """, [
                description.description,
                description.id
            ]).fetchone()

            return Description(
                id=desc[0],
                description=desc[1],
                version=desc[2],
                labels=save_labels(description.id, description.labels) if description.labels else []
            )


def save_descriptions(action_id: int, descriptions: list[Description]) -> None:
    return [save_description(action_id, desc) for desc in descriptions if desc.description]


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

        descriptions = save_descriptions(action_id, action.descriptions)

        return Action(
            id=action_id,
            project_id=action.project_id,
            datetime=datetime.now(),
            operation=action.operation,
            file_column=action.file_column,
            active_description=len(descriptions) - 1,
            active_labels=len(descriptions[-1].labels) - 1 if descriptions else 0,
            descriptions=descriptions
        )
    

async def generate_action_labels(action: Action, user_id: UUID) -> Description:
    """Generate labels for an action."""

    # Only provide column if operation is not Entity Matching
    data_ts = await get_file_data_tableswift(action.project_id, user_id, action.file_column if action.operation.id != 4 else None)

    input = {
        "function": OPERATIONS[action.operation.id],
        "column": action.file_column,
        "description": action.descriptions[action.active_description].description,
        "data": data_ts
    }
    print("Input for label generation:", input)

    # Call the TableSwift framework to generate labels
    # TODO add column name to input
    ts.configure(api_key=settings.LLM_API_KEY)
    labeled_data = ts.generate_labels(instruction=input["description"], task=input["function"], demonstrations=[], samples_to_label=input["data"])

    output = [
        [{action.file_column: label["Input"]}, {"Label": label["Output"]}] for label in labeled_data
    ]
    print("Generated labels:", output)

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

    return Description(
        id=saved_action.descriptions[action.active_description].id,
        description=saved_action.descriptions[action.active_description].description,
        version=next_version,
        labels=saved_action.descriptions[action.active_description].labels + [
            Labels(
                id=result[0],
                json=json.dumps(output),
                version=next_version,
                codes=[]
            )
        ]
    )


def update_labels(labels: Labels) -> None:
    """Update labels for an action."""
    with get_db() as conn:
        # Check if the label exists
        existing_labels = conn.execute("""
            SELECT id FROM labels WHERE id = ?
        """, [labels.id]).fetchone()

        if not existing_labels:
            raise ValueError("Label not found")

        # If it exists, update it
        conn.execute("""
            UPDATE labels SET 
                json = ?
            WHERE id = ?
        """, [
            json.dumps(labels.json),
            labels.id
        ])

def generate_action_code(action: Action) -> None:
    """Generate code for an action."""
    input = {
        "function": OPERATIONS[action.operation.id],
        "column": action.file_column,
        "description": action.descriptions[action.active_description].description,
        "labels": format_data_tableswift(action.descriptions[action.active_description].labels[action.active_labels].json, action.file_column),
    }
    print("Input for code generation:", input)

    # Call the TableSwift framework to generate code
    ts.configure(api_key=settings.LLM_API_KEY)
    code, router_code = ts.generate_code(instruction=input["description"],
                    task=input["function"],
                    samples=input["labels"],
                    lang="python",
                    num_trials=1,
                    num_retry=1,
                    num_iterations=1)
    
    print("Generated code:", code)
    print("Generated router code:", router_code)

    # TODO remove if generation works properly
    if not router_code:
        router_code = "def validate(input_string): return True"

    saved_action = update_action(action.id, action)

    with get_db() as conn:
        # First get the next version number
        version_result = conn.execute("""
            SELECT COALESCE(MAX(version) + 1, 1)
            FROM codes
            WHERE label_id = ?
        """, [saved_action.descriptions[action.active_description].labels[action.active_labels].id]).fetchone()
        next_version = version_result[0]

        # Then do the insert
        result = conn.execute("""
            INSERT INTO codes (code, router_code, label_id, version)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """, [
            code,
            router_code,
            saved_action.descriptions[action.active_description].labels[action.active_labels].id,
            next_version
        ]).fetchone()

    return Code(
        id=result[0],
        code=code,
        router_code=router_code,
        version=next_version
    )


def update_code(code: Code) -> None:
    """Update code for an action."""
    with get_db() as conn:
        # Check if the code exists
        existing_code = conn.execute("""
            SELECT id FROM codes WHERE id = ?
        """, [code.id]).fetchone()

        print(existing_code)

        if not existing_code:
            raise ValueError("Code not found")

        # If it exists, update it
        conn.execute("""
            UPDATE codes SET 
                code = ?
            WHERE id = ?
        """, [
            code.code,
            code.id
        ])


async def execute_code(action: Action, user_id: UUID) -> File:
    input = {
        "function": OPERATIONS[action.operation.id],
        "column": action.file_column,
        "description": action.descriptions[action.active_description].description,
        "labels": format_data_tableswift(action.descriptions[action.active_description].labels[action.active_labels].json, action.file_column),
        "code": action.descriptions[action.active_description].labels[action.active_labels].codes[action.active_code].code,
        "router_code": action.descriptions[action.active_description].labels[action.active_labels].codes[action.active_code].router_code,
        "data": await get_file_data_tableswift(action.project_id, user_id, action.file_column if action.operation.id != 4 else None)
    }
    print("Input for code execution:", input)
    
    ts.configure(api_key=settings.LLM_API_KEY)
    results, invalid_data = ts.execute_code(input["code"],
        instruction=input["description"],
        task=input["function"],
        lang="python",
        inputs=input["data"],
        samples=input["labels"],
        router_code=input["router_code"]
    )

    print("Execution results:", results)
    print("Invalid data:", invalid_data)

    # Get the file path for this action
    with get_db() as conn:
        file_result = conn.execute("""
            SELECT f.file_path
            FROM actions a
            JOIN projects p ON a.project_id = p.id
            JOIN files f ON p.file_id = f.id
            WHERE a.id = ?
        """, [action.id]).fetchone()
        
        if not file_result:
            raise ValueError("File not found for this action")
        
        original_file_path = file_result[0]

    # Extract new values from results
    new_values = [result['Output'] for result in results]

    print("New values to be written:", new_values)
    
    # Process file changes and generate diff
    new_file = await process_file_changes(
        original_file_path=original_file_path,
        column_name=action.file_column,
        new_values=new_values,
        action_id=action.id,
        project_id=action.project_id
    )
    print("New file path:", new_file)

    return new_file

def check_action_ownership(action_id: int, user_id: UUID) -> bool:
    """
    Check if an action belongs to a user by verifying project ownership.
    Returns True if the action belongs to the user, False otherwise.
    """
    with get_db() as conn:
        result = conn.execute("""
            SELECT 1
            FROM actions a
            JOIN projects p ON a.project_id = p.id
            WHERE a.id = ? AND p.user_id = ?
        """, [action_id, user_id]).fetchone()
        
        return result is not None


def check_label_ownership(label_id: int, user_id: UUID) -> bool:
    """
    Check if a label belongs to a user by verifying the ownership chain:
    label -> description -> action -> project -> user
    Returns True if the label belongs to the user, False otherwise.
    """
    with get_db() as conn:
        result = conn.execute("""
            SELECT 1
            FROM labels l
            JOIN description d ON l.description_id = d.id
            JOIN actions a ON d.action_id = a.id
            JOIN projects p ON a.project_id = p.id
            WHERE l.id = ? AND p.user_id = ?
        """, [label_id, str(user_id)]).fetchone()
        
        return result is not None


def check_code_ownership(code_id: int, user_id: UUID) -> bool:
    """
    Check if a code record belongs to a user by verifying the ownership chain:
    code -> label -> description -> action -> project -> user
    Returns True if the code belongs to the user, False otherwise.
    """
    with get_db() as conn:
        result = conn.execute("""
            SELECT 1
            FROM codes c
            JOIN labels l ON c.label_id = l.id
            JOIN description d ON l.description_id = d.id
            JOIN actions a ON d.action_id = a.id
            JOIN projects p ON a.project_id = p.id
            WHERE c.id = ? AND p.user_id = ?
        """, [code_id, str(user_id)]).fetchone()
        
        return result is not None
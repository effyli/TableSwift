from ..database import get_db
from ..models.operation import Operation
from typing import List

def get_operations() -> List[Operation]:
    """Get all operations from the database."""
    with get_db() as conn:
        results = conn.execute("""
            SELECT id, name
            FROM operations
            ORDER BY name ASC
        """).fetchall()
        
        return [
            Operation(
                id=row[0],
                name=row[1]
            )
            for row in results
        ]

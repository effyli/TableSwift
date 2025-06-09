# DuckDB NL2SQL formatter

def format_model_output_sql(output_sql: str) -> str:
        def clean_code_block(block: str) -> str:
            """Clean a code block by removing markdown syntax and extra whitespace."""
            # Remove markdown indicators and common SQL prefixes
            cleaned = (block
                       .replace('```sql\n', '')
                       .replace('```duckdb\n', '')
                       .replace('```\n', '')
                       .replace('```', '')
                       .strip())

            return cleaned

        def ensure_semicolon(sql: str) -> str:
            """Ensure the SQL query ends with exactly one semicolon."""
            sql = sql.strip()
            # Remove any existing trailing semicolons
            while sql.endswith(';'):
                sql = sql[:-1].strip()
            # Add back exactly one semicolon
            return sql + ";"

        # First, try to find SQL-specific code blocks
        sql_blocks = []
        start_pos = 0
        while True:
            start = output_sql.find('```sql', start_pos)
            if start == -1:
                start = output_sql.find('```duckdb', start_pos)
            if start == -1:
                break

            end = output_sql.find('```', start + 4)
            if end == -1:
                break

            sql_blocks.append(output_sql[start:end+3])
            start_pos = end + 3

        # If SQL blocks found, use the last one
        if sql_blocks:
            return ensure_semicolon(clean_code_block(sql_blocks[-1])).replace('```sql','').replace('```','').strip()

        # If no SQL blocks, look for generic code blocks
        generic_blocks = []
        start_pos = 0
        while True:
            start = output_sql.find('```', start_pos)
            if start == -1:
                break

            end = output_sql.find('```', start + 3)
            if end == -1:
                break

            block = output_sql[start:end+3]
            # Skip if this is actually an SQL block (we already handled those)
            if not block.startswith('```sql') and not block.startswith('```duckdb'):
                generic_blocks.append(block)
            start_pos = end + 3

        # If generic blocks found, use the last one
        if generic_blocks:
            return ensure_semicolon(clean_code_block(generic_blocks[-1])).replace('```sql','').replace('```','').strip()

        # If no code blocks found at all, take everything up to first semicolon
        semicolon_pos = output_sql.find(';')
        if semicolon_pos != -1:
            return ensure_semicolon(output_sql[:semicolon_pos].strip()).replace('```sql','').replace('```','').strip()

        # If no semicolon found, use the entire text
        return ensure_semicolon(output_sql.strip()).replace('```sql','').replace('```','').strip()


def format_model_output_python(output_python: str) -> str:
    def clean_code_block(block: str) -> str:
        """Clean a code block by removing markdown syntax and extra whitespace."""
        # Remove markdown indicators and common Python prefixes
        cleaned = (block
                    .replace('```python\n', '')
                    .replace('```Python\n', '')
                    .replace('```\n', '')
                    .replace('```', '')
                    .strip())

        return cleaned

        # def ensure_semicolon(python_code: str) -> str:
        #     """Ensure the Python ends with exactly one semicolon."""
        #     python_code = python_code.strip()
        #     # Remove any existing trailing semicolons
        #     while python_code.endswith(';'):
        #         python_code = python_code[:-1].strip()
        #     # Add back exactly one semicolon
        #     return python_code + ";"

        # First, try to find Python-specific code blocks
    python_blocks = []
    start_pos = 0
    while True:
        start = output_python.find('```python', start_pos)
        if start == -1:
            start = output_python.find('```Python', start_pos)
        if start == -1:
            break

        end = output_python.find('```', start + 4)
        if end == -1:
            break

        python_blocks.append(output_python[start:end+3])
        start_pos = end + 3

    # If SQL blocks found, use the last one
    if python_blocks:
        return (clean_code_block(python_blocks[-1])).replace('```Python','').replace('```','').strip()

    # If no SQL blocks, look for generic code blocks
    generic_blocks = []
    start_pos = 0
    while True:
        start = output_python.find('```', start_pos)
        if start == -1:
            break

        end = output_python.find('```', start + 3)
        if end == -1:
            break

        block = output_python[start:end+3]
        # Skip if this is actually an SQL block (we already handled those)
        if not block.startswith('```python') and not block.startswith('```Python'):
            generic_blocks.append(block)
        start_pos = end + 3

    # If generic blocks found, use the last one
    if generic_blocks:
        return clean_code_block(generic_blocks[-1]).replace('```python','').replace('```','').strip()

    # # If no code blocks found at all, take everything up to first semicolon
    # semicolon_pos = output_python.find(';')
    # if semicolon_pos != -1:
    #     return output_sql[:semicolon_pos].strip().replace('```sql','').replace('```','').strip()

    # If no semicolon found, use the entire text
    return output_python.strip().replace('```python','').replace('```','').strip()


# model_output = """```python
# def string_transformation(input_string):
#     input_value = int(input_string.replace(' mg', ''))
#     output_value = input_value * 2
#     return f"{output_value} ml"
# ```"""
# print("here is the result")
# print(format_model_output_python(model_output))
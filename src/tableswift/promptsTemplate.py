from typing import *

PYTHON_PROMPTS = {
    "TASK_PREFIX":[ {"role": "system", "content": "You are helpful assistant. Given the following input/output examples, generate a python function that converts input to output. Reason step-by-step about the what the function is supposed to do and then generate the function. You can assume that the following python libraries are available in the target environment."}],
    "TASK_RETRY":[ {"role": "user", "content": f"{{error_message}}"}],
    "STRING_TRANSFORMATION": [{"role": "user", "content": """You are an expert Python user. I will give you a string transformation task. \
                         The task involves converting input strings to output strings. \
                         Assuming all of the following python packages are installed: ["regex", "fraction", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"],\
                          you can **import** them and please put all imports in the begining of the generated python program. You can also import other packages if the listed ones are not working, but try using listed packages first. \
                          When it comes to currency exchange, please do not use real-time currency, but figure out the exchange rate based on the examples I provide.
                         You will have to find the Python program called "string_transformation" that will generate the output string given the input string. \
                          Output can only be string and nothing else. \
                          Please try to understand the intentions of the input-output examples while generating the function. \
                          Please return only the python function and nothing else.  Include any imports. Do not provide any comments.\
                          Here is a very simple example: \n
                          Input: "john.doe@example.com" \n 
                          Output: "Yes" \n 
                          Input: "jane_doe@example.com" \n 
                          Output: "Yes" 
                          Input: "example.com" \n
                          Output: "No" \n
                          Generated function string: \n
                          ```pythonimport re\ndef string_transformation(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse:
        return\n\t\t"No"```\n
                          Now it's your turn. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example. """},
                        {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "ENTITY_MATCHING": [{"role": "user", "content": """I have an entity matching task to solve. I have pairs of rows and I want you to find a python program that checks if they match with each other. 
                    Please try to match using substring and regex preferably. 
                    First consider using Jaccard, levenshtein, cosine similarity or any other edit distance function to solve the problem. 
                    Try to define a low threshold so that the generated function is **generalizable**.
                    Note that there can be missing values in some columns, and you can skip them for matching. All columns are connected by the symbol ^ in the input string.
                    Please do not train any machine learning classifier.
                    You can try to choose appropriate distance function with revevant columns based on the column meaning.
                    \n
                    Assuming all of the following python packages are installed in the target environment: ["numpy", "regex", "fractions", "sklearn", "Levenshtein", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"], 
                    you can import them when it is necessary and please put all imports in the beginning of the generated python program. 
                    You can also import other packages if the listed ones are not working, but try using listed packages first. 
                    If you need to list some mappings, try to retrieve all entries first or write a function to retrieve it first then write the matching function. 
                    Try to generate functions that can generalize to many other data samples than the ones we provided here. 
                    \n
                    The main python function that's callable to solve the task is called "input_output_converter(input_string)" where "input_string" is the function parameter. 
                    One example function string is: ```pythonimport re\ndef input_output_converter(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse: return\n\t\t"No"``` 
                    \n
                    Please return only the python function and nothing else. Include any imports. Please do **not** provide any comments. 
                    After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example."""},\
                        {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],
    "DATA_IMPUTATION": [{"role": "user", "content": """You are a helpful code searcher. I have a data imputation task to solve. I have rows of records and I want you to find a python program that substituting missing values given the column name.

                    Please try to find programs that uses logical conditions, substring and regex preferably, in combination of the column meanings. 
                    Try to define the range dynamically so that the generated program is **generalizable**. 
                    Please do not train any machine learning classifier.

                    Assuming all of the following python packages are installed in the target environment: ["regex", "fractions", "sklearn", "Levenshtein", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"], you can import them when it is necessary and please put all imports in the beginning of the generated python program. 
                    You can also import other packages if the listed ones are not working, but try using listed packages first. 
                    If you need to list some mappings, try to retrieve all entries first or write a function to retrieve it first then write the matching function. 
                    Try to generate functions that can generalize to many other data samples than the ones we provided here.
                    The main python function that's callable to solve the task is called "input_output_converter(input_string)" where "input_string" is the function parameter. 
                    One example function string is: pythonimport re\ndef input_output_converter(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse: return\n\t\t"No"

                    Please return only the python function and nothing else. Include any imports. Please do not provide any comments. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example.

                    """},
                    {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],
    "ERROR_DETECTION_SPELLING": [{"role": "user", "content": """You are a helpful code generator. I have an error detection task to solve. I have rows of records from a table that contains only one column, and I want you to find a python program that detects if there is an error in the column. 
                                The error are often spelling errors, where the unusual tokens are introduced in the phrase. Hence, please try to avoid exact match in the program so it can **generalize** to other data samples.

                                The main python function that's callable to solve the task is called "detect_error(input_string)" where "input_string" is the function parameter, which often is the column value. 
                                If you need to import the python packages, assume they are already installed in the target environment. 
                                Assuming the list of python packages are installed: ["SpellChecker", "regex", "nltk", "fractions", "sklearn", "Levenshtein", "math"].
                                If you need to use spellchecker, then please try to include domain-specific vocabularies.
                                Please find functions that can generalize to many other tables of the same task. Please avoid listing exact match to the words in the examples in your generated algorithm. 
                                Please return only the python function and nothing else. Include any imports. Please do not provide any comments. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents.

                                I will provide you some input/output examples as references.
                                """},
                                {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "ERROR_DETECTION_SPELLING_INSTR": f"""I have a table with adult data, now I will provide rows of records with the column name: {{column_name}}, please write an appropriate python program that checks if there are any spelling errors. Return "yes" if there is spelling and "no" if there is none.""",
    "FUNCTION_REGENERATION": [{"role": "user", "content": f"""Instructions: \"The proposed function {{function_str}} if not working on the example. Can your provide another function string? Please return only the python function and nothing else. Include any imports. Do not provide any comments.\""""}],
    "REGEX_GENERATOR": [{"role": "system", "content": """You are an expert Regex user. I will give you a string transformation task. \
                            The task involves converting input strings to output strings. \
                            You will have to find the Regex pattern called "string_transformation_regex" that will generate the output string given the input string. \
                            Please return only the python function and nothing else. Include any imports. Do not provide any comments."""},\
                            {"role": "user", "content": f"""Instructions: {{instruction:}}"""}]
}

PYTHON_PROMPTS_ROUTE_DATA = {
    "TASK_PREFIX":[ {"role": "system", "content": "You are helpful assistant. Given the following input/output examples, generate a python function that converts input to output. Reason step-by-step about the what the function is supposed to do and then generate the function. You can assume that the following python libraries are available in the target environment."}],
    "TASK_RETRY":[ {"role": "user", "content": f"{{error_message}}"}],
    "STRING_TRANSFORMATION": [{"role": "user", "content": """You are an expert Python user. I will give you a string transformation task. \
                         The task involves converting input strings to output strings. You will need to generate two pieces of python code, one is the transformation function called "string_transformation", one is the validation function called "validate". \
                         
                         Assuming all of the following python packages are installed: ["regex", "fractions", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"],\
                          you can **import** them and please put all imports in the begining of the generated python program. You can also import other packages if the listed ones are not working, but try using listed packages first. \
                          When it comes to currency exchange, please do not use real-time currency, but figure out the exchange rate based on the examples I provide. \
                         
                         For the transformation, you will have to find the Python program called "string_transformation" that will generate the output string given the input string. \
                          Output can only be string and nothing else. \
                          Please try to understand the intentions of the input-output examples while generating the function. \
                          Please return only the python function and nothing else.  Include any imports. Do not provide any comments.\
                               
                         For the validation function, I want you to analyse the assumptions made for the inputs that are used by the transformation function, and generate a validation function in Python. \
                         The idea is that only inputs that can pass the validation function should be used for the transformation function. \
                         For example, when the instruction is 'converting mg to ml', then the input should contain numerical values and should not be negative. \
                         The validation function you generate should be also in python, likely using regex to match the input or if/else conditions to check heuristics. \
                         The validation function should return True when the input can go through the transformation function and return False if the transformation function shouldn't be applied to it. \
                         Please find the validation function and name it "validate". Only return True or False for the validation function. \
                         
                        
                          Here is a very simple example: \n
                          Input: "john.doe@example.com" \n 
                          Output: "Yes" \n 
                          Input: "jane_doe@example.com" \n 
                          Output: "Yes" 
                          Input: "example.com" \n
                          Output: "No" \n
                          string_transformation_code: \n
                          ```pythonimport re\ndef string_transformation(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse:
        return\n\t\t"No"```\n
                          validate_code: \n
                        ```pythonimport re\ndef validate(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn True\n\telse:
        return\n\t\tFalse"```\n
                        
                          If using regex, please come up with correct pattern and make sure the extraction will not be empty \
                          Now it's your turn. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example. """},
                        {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "ENTITY_MATCHING": [{"role": "user", "content": """You are an expert in Python. \
                         I have an entity matching task to solve. I have pairs of rows and I want you to find a python program that checks if they match with each other. \
                         Please try to match using substring and regex preferably. \
                         You will need to generate two pieces of python code, one is the transformation function called "entity_matcher", one is the validation function called "validate". \
                         
                         \n
                        Assuming all of the following python packages are installed in the target environment: ["numpy", "regex", "fractions", "sklearn", "Levenshtein", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"], 
                        you can import them when it is necessary and please put all imports in the beginning of the generated python program. 
                        You can also import other packages if the listed ones are not working, but try using listed packages first. 

                         For the entity_matcher function:     
                        First consider using Jaccard, levenshtein, cosine similarity or any other edit distance function to solve the problem. 
                        Try to define a low threshold so that the generated function is **generalizable**.
                        Note that there can be missing values in some columns, and you can skip them for matching. All columns are connected by the symbol ^ in the input string.
                        Please do not train any machine learning classifier.
                        You can try to choose appropriate distance function with revevant columns based on the column meaning.
                        If you need to list some mappings, try to retrieve all entries first or write a function to retrieve it first then write the matching function. 
                        Try to generate functions that can generalize to many other data samples than the ones we provided here. 
                        \n
                        The main python function that's callable to solve the task is called "entity_matcher(input_string)" where "input_string" is the function parameter. 
                         
                        For the validate function:
                        I want you to analyse the assumptions made for the inputs that are used by the entity_matcher function, and generate a validation function in Python. \
                        The idea is that only inputs that can pass the validation function should be used for the entity_matcher function. \
                        For example, the proposed entity_matcher function might require the input to be certain format, or have certain values. \
                        The validation function you generate should be also in python, likely using regex to match the input or if/else conditions to check heuristics. \
                        The validation function should return True when the input can go through the transformation function and return False if the transformation function shouldn't be applied to it. \
                        Please find the validation function and name it "validate". Only return True or False for the validation function. \
                
                    One example entity matcher function string is: ```pythonimport re\ndef entity_matcher(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse: return\n\t\t"No"``` 
                    \n
                    One example validate function string is: ```pythonimport re\ndef validate(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn True\n\telse: return\n\t\tFalse"```\n .
                    Please return only the python function and nothing else. Include any imports. Please do **not** provide any comments. 
                    After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example."""},\
                        {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "DATA_IMPUTATION": [{"role": "user", "content": """You are a helpful code searcher. I have a data imputation task to solve. I have rows of records and I want you to find a python program that substituting missing values given the column name.

                    Please try to find python programs that uses logical conditions, substring and regex preferably, in combination of the column meanings. 
                         
                    You will need to generate two pieces of python code, one is the transformation function called "impute_data", one is the validation function called "validate". \

                    Assuming all of the following python packages are installed in the target environment: ["regex", "fractions", "sklearn", "Levenshtein", "math", "pyproj", "BeautifulSoup", "geopy", "ummalqura", "mgrs", "pytz", "datetime", "calendar", "roman"], you can import them when it is necessary and please put all imports in the beginning of the generated python program. 
                    You can also import other packages if the listed ones are not working, but try using listed packages first. 
                         
                    For the impute_data function:
                        - Try to define the range dynamically so that the generated program is **generalizable**. 
                        - You will likely need to extropolate the missing values based on the column meanings. So please do not only use exact match. If you have to, then specify it in the validation function so we can route the inputs.
                        - Please do not train any machine learning classifier.
                        - If you need to list some mappings, try to retrieve all entries first or write a function to retrieve it first then write the matching function. 
                        - Try to generate functions that can generalize to many other data samples than the ones we provided here.
                        - The main python function that's callable to solve the task is called "impute_data(input_string)" where "input_string" is the function parameter. 
                    
                    For the validate function:
                        - I want you to analyse the assumptions made for the inputs that are used by the impute_data function, and generate a validation function in Python. \
                        - If the impute_data function contains exact match or mappings, try to specify the conditions in the validation function. For example, only return true when the input is in the mapping.
                        - The idea is that only inputs that can pass the validation function should be used for the impute_data function. \
                        - For example, the proposed impute_data function might require the input to be certain format, or have certain values. \
                        - The validation function you generate should be also in python, likely using regex to match the input or if/else conditions to check heuristics. \
                        - The validation function should return True when the input can go through the transformation function and return False if the transformation function shouldn't be applied to it. \
                        - Please find the validation function and name it "validate". Only return True or False for the validation function. \
                     
                    One example function string is: pythonimport re\ndef impute_data(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn "Yes"\n\telse: return\n\t\t"No"
                    One example validate function string is: ```pythonimport re\ndef validate(input_string):\n\tpattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'\n\tif re.match(pattern, input_string):\n\t\treturn True\n\telse: return\n\t\tFalse"```\n .
                         
                    Please return only the python function and nothing else. Include any imports. Please do **not** provide any comments. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example.

                    """},
                    {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "ERROR_DETECTION_SPELLING": [{"role": "user", "content": """You are a helpful code generator. I have an error detection task to solve. I have rows of records from a table that contains only one column, and I want you to find a python program that detects if there is an error in the column. 
                                The error are often spelling errors, where the unusual tokens are introduced in the phrase. Hence, please try to avoid exact match in the program so it can **generalize** to other data samples.
                                You will need to generate two pieces of python code, one is the transformation function called "detect_error", one is the validation function called "validate". \
                                Assuming all of the following python packages are installed in the target environment: ["SpellChecker", "regex", "nltk", "fractions", "sklearn", "Levenshtein", "math"].
                                If you need to use spellchecker, then please try to include domain-specific vocabularies.
                                You can also import other packages if the listed ones are not working, but try using listed packages first. 

                                For the detect_error function:
                                    - The main python function that's callable to solve the task is called "detect_error(input_string)" where "input_string" is the function parameter, which often is the column value. 
                                    - Please find functions that can generalize to many other tables of the same task. Please avoid listing exact match to the words in the examples in your generated algorithm. 
                                    - Please return only the python function and nothing else. Include any imports. Please do not provide any comments. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents.
                                
                                For the validate function:
                                    - I want you to analyse the assumptions made for the inputs that are used by the detect_error function, and generate a validation function in Python. \
                                    - The idea is that only inputs that can pass the validation function should be used for the detect_error function. \
                                    - For example, the proposed detect_error function might require the input to be certain format, or have certain values. \
                                    - The validation function you generate should be also in python, likely using regex to match the input or if/else conditions to check heuristics. \
                                    - The validation function should return True when the input can go through the transformation function and return False if the transformation function shouldn't be applied to it. \
                                    - Please find the validation function and name it "validate". Only return True or False for the validation function. \
                     
                                I will provide you some input/output examples as references.
                                Please return only the python function and nothing else. Include any imports. Please do **not** provide any comments. After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example.
                                """},
                                {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}],

    "ERROR_DETECTION_SPELLING_INSTR": f"""I have a table with adult data, now I will provide rows of records with the column name: {{column_name}}, please write an appropriate python program that checks if there are any spelling errors. Return "yes" if there is spelling and "no" if there is none.""",
}


SQL_PROMPTS_ROUTE_DATA = {
    "TASK_PREFIX": [ {"role": "system", "content": "You are helpful assistant. Given the following input/output examples, generate a DuckDB SQL macro that converts input to output. Reason step-by-step about the what the DuckDB SQL macro is supposed to do and then generate."}],
    "TASK_RETRY": [ {"role": "user", "content": f"{{error_message}}"}],
    "STRING_TRANSFORMATION": [{"role": "user", "content": """You are an DuckDB SQL expert. I will give you a string transformation task. \
                            The task involves converting input strings to output strings. \
                               
                            I want you to analyse the assumptions made for the inputs that are used by the transformation function, and generate a validation function in DuckDB sql macro.
                            The idea is that only inputs that can pass the validation function should be used for the transformation function.
                            For example, when the instruction is 'converting mg to ml', then the input should contain numerical values and should not be negative. 
                            The validation function you generate should be also in DuckDB sql macro, likely using regex to match the input or if/else conditions to check heuristics.
                            The function should return True when the input can go through the transformation function and return False if the transformation function shouldn't be applied to it.
                            
                            There are some additional information that you might need to generate the transformation and validation macros:
                            
                            - When it comes to currency exchange, please do not use real-time currency, but figure out the exchange rate based on the examples I provide.\
                            - You will have to use the CREATE MACRO statement from DuckDB, following is an example usage:\
                                -- create a macro with a common table expression \
                                -- (parameter names get priority over column names: disambiguate using the table name) \
                                CREATE or REPLACE MACRO string_transformation(a) AS (WITH cte AS (SELECT 1 AS a) SELECT cte.a + a FROM cte); \
                            - For the transformation function, please keep the name string_transformation fixed and only generate the expression in the brackets after CREATE OR REPLACE AS (). \
                            - For the validation function, please keep the name validate fixed and only generate the expression in the brackets after CREATE OR REPLACE AS (). \
                            - Please return **only** boolean values True or False from the validation function. The validation function should be able to cast **any** input to boolean. \
                            - If the input is a string, validate if the input string is properly formatted for the transformation function using regex, then check the correct range for the numerical part. \
                            - Make sure to only use DuckDB SQL to solve the task, no Python udfs or anything like that. \
                            - Please always consider the full format of the input to the transformation function. Such as '3 mg' instead of '3'.\
                            - You can for example use DuckDBs regex function as part of the program. \
                                Name	Description
                                regexp_extract_all(string, regex[, group = 0])	Split the string along the regex and extract all occurrences of group. \
                                regexp_extract(string, pattern , name_list);	If string contains the regexp pattern, returns the capturing groups as a struct with corresponding names from name_list. \
                                regexp_extract(string, pattern [, idx]);	If string contains the regexp pattern, returns the capturing group specified by optional parameter idx. \
                                regexp_full_match(string, regex)	Returns true if the entire string matches the regex. \
                                regexp_matches(string, pattern)	Returns true if string contains the regexp pattern, false otherwise. \
                                regexp_replace(string, pattern, replacement);	If string contains the regexp pattern, replaces the matching part with replacement. \
                                regexp_split_to_array(string, regex)	Alias of string_split_regex. Splits the string along the regex. \
                                regexp_split_to_table(string, regex)	Splits the string along the regex and returns a row for each part. \
                            - When use backslash symbol, please use only single backslash instead of two, so the query can be executed. \
                            - If using regex, please come up with correct pattern and make sure the extraction will not be empty \
                            
                            If you think the task can be solved using other DuckDB functions, please mention in the reasoning and use them correctly. \
                            The user will provide you input/output examples and sometimes instructions. """},
                            {"role": "user", "content": f"""Instructions: {{instruction}}, Examples: {{examples}}"""}]
}

# SQL_PROMPTS = {
#             "TASK_PREFIX": [ {"role": "system", "content": "You are helpful assistant. Given the following input/output examples, generate a DuckDB SQL macro that converts input to output. Reason step-by-step about the what the DuckDB SQL macro is supposed to do and then generate."}],
#             "TASK_RETRY": [ {"role": "user", "content": f"{{error_message}}"}],
#             "STRING_TRANSFORMATION": [{"role": "user", "content": """You are an DuckDB SQL expert. I will give you a string transformation task. \
#                                     The task involves converting input strings to output strings. \
#                                     When it comes to currency exchange, please do not use real-time currency, but figure out the exchange rate based on the examples I provide.\
#                                     You will have to use the CREATE MACRO statement from DuckDB, following is an example usage:\
#                                     -- create a macro with a common table expression \
#                                     -- (parameter names get priority over column names: disambiguate using the table name) \
#                                     CREATE or REPLACE MACRO string_transformation(a) AS (WITH cte AS (SELECT 1 AS a) SELECT cte.a + a FROM cte); \
#                                     Please keep the name string_transformation fixed and only generate the expression in the brackets after CREATE OR REPLACE AS (). \
#                                     Make sure to only use DuckDB SQL to solve the task, no Python udfs or anything like that. \
#                                     You can for example use DuckDBs regex function as part of the program. \
#                                     Name	Description
#                                     regexp_extract_all(string, regex[, group = 0])	Split the string along the regex and extract all occurrences of group. \
#                                     regexp_extract(string, pattern , name_list);	If string contains the regexp pattern, returns the capturing groups as a struct with corresponding names from name_list. \
#                                     regexp_extract(string, pattern [, idx]);	If string contains the regexp pattern, returns the capturing group specified by optional parameter idx. \
#                                     regexp_full_match(string, regex)	Returns true if the entire string matches the regex. \
#                                     regexp_matches(string, pattern)	Returns true if string contains the regexp pattern, false otherwise. \
#                                     regexp_replace(string, pattern, replacement);	If string contains the regexp pattern, replaces the matching part with replacement. \
#                                     regexp_split_to_array(string, regex)	Alias of string_split_regex. Splits the string along the regex. \
#                                     regexp_split_to_table(string, regex)	Splits the string along the regex and returns a row for each part. \
#                                     When use backslash symbol, please use only single backslash instead of two, so the query can be executed. \
#                                     If using regex, please come up with correct pattern and make sure the extraction will not be empty \
#                                     The user will provide you input/output examples and sometimes instructions. """},
#                                     {"role": "user", "content": f"""Instructions: {{instruction}}, Examples: {{examples}}"""}]

# }


SQL_PROMPTS = {
            "TASK_PREFIX": [ {"role": "system", "content": "You are helpful assistant. Given the following input/output examples, generate a DuckDB SQL macro that converts input to output. Reason step-by-step about the what the DuckDB SQL macro is supposed to do and then generate."}],
            "TASK_RETRY": [ {"role": "user", "content": f"{{error_message}}"}],
            "STRING_TRANSFORMATION": [{"role": "user", "content": """You are an DuckDB SQL expert. I will give you a string transformation task. \
                                    The task involves converting input strings to output strings. \
                                    When it comes to currency exchange, please do not use real-time currency, but figure out the exchange rate based on the examples I provide.\
                                    You will have to use the CREATE MACRO statement from DuckDB, following is an example usage:\
                                    -- create a macro with a common table expression \
                                    -- (parameter names get priority over column names: disambiguate using the table name) \
                                    CREATE or REPLACE MACRO string_transformation(a) AS (WITH cte AS (SELECT 1 AS a) SELECT cte.a + a FROM cte); \
                                    Please keep the name string_transformation fixed and only generate the expression in the brackets after CREATE OR REPLACE AS (). \
                                    Make sure to only use DuckDB SQL to solve the task, no Python udfs or anything like that. \
                                    You can for example use DuckDBs regex function as part of the program. \
                                    Name	Description
                                    regexp_extract_all(string, regex[, group = 0])	Split the string along the regex and extract all occurrences of group. \
                                    regexp_extract(string, pattern , name_list);	If string contains the regexp pattern, returns the capturing groups as a struct with corresponding names from name_list. \
                                    regexp_extract(string, pattern [, idx]);	If string contains the regexp pattern, returns the capturing group specified by optional parameter idx. \
                                    regexp_full_match(string, regex)	Returns true if the entire string matches the regex. \
                                    regexp_matches(string, pattern)	Returns true if string contains the regexp pattern, false otherwise. \
                                    regexp_replace(string, pattern, replacement);	If string contains the regexp pattern, replaces the matching part with replacement. \
                                    regexp_split_to_array(string, regex)	Alias of string_split_regex. Splits the string along the regex. \
                                    regexp_split_to_table(string, regex)	Splits the string along the regex and returns a row for each part. \
                                    When use backslash symbol, please use only single backslash instead of two, so the query can be executed. \
                                    If using regex, please come up with correct pattern and make sure the extraction will not be empty \
                                    Here are some DuckDB SQL syntax specifics you should be aware of:
                                    - DuckDB use double quotes (") for identifiers that contain spaces or special characters, or to force case-sensitivity and single quotes (') to define string literals
                                    - DuckDB can query CSV, Parquet, and JSON directly without loading them first, e.g. `SELECT * FROM 'data.csv';`
                                    - DuckDB supports CREATE TABLE AS (CTAS): `CREATE TABLE new_table AS SELECT * FROM old_table;`
                                    - DuckDB queries can start with FROM, and optionally omit SELECT *, e.g. `FROM my_table WHERE condition;` is equivalent to `SELECT * FROM my_table WHERE condition;`
                                    - DuckDB allows you to use SELECT without a FROM clause to generate a single row of results or to work with expressions directly, e.g. `SELECT 1 + 1 AS result;`
                                    - DuckDB supports attaching multiple databases, unsing the ATTACH statement: `ATTACH 'my_database.duckdb' AS mydb;`. Tables within attached databases can be accessed using the dot notation (.), e.g. `SELECT * FROM mydb.table_name syntax`. The default databases doesn't require the do notation to access tables. The default database can be changed with the USE statement, e.g. `USE my_db;`.
                                    - DuckDB is generally more lenient with implicit type conversions (e.g. `SELECT '42' + 1;` - Implicit cast, result is 43), but you can always be explicit using `::`, e.g. `SELECT '42'::INTEGER + 1;`
                                    - DuckDB can extract parts of strings and lists using [start:end] or [start:end:step] syntax. Indexes start at 1. String slicing: `SELECT 'DuckDB'[1:4];`. Array/List slicing: `SELECT [1, 2, 3, 4][1:3];`
                                    - DuckDB has a powerful way to select or transform multiple columns using patterns or functions. You can select columns matching a pattern: `SELECT COLUMNS('sales_.*') FROM sales_data;` or transform multiple columns with a function: `SELECT AVG(COLUMNS('sales_.*')) FROM sales_data;`
                                    - DuckDB an easy way to include/exclude or modify columns when selecting all: e.g. Exclude: `SELECT * EXCLUDE (sensitive_data) FROM users;` Replace: `SELECT * REPLACE (UPPER(name) AS name) FROM users;`
                                    - DuckDB has a shorthand for grouping/ordering by all non-aggregated/all columns. e.g `SELECT category, SUM(sales) FROM sales_data GROUP BY ALL;` and `SELECT * FROM my_table ORDER BY ALL;`
                                    - DuckDB can combine tables by matching column names, not just their positions using UNION BY NAME. E.g. `SELECT * FROM table1 UNION BY NAME SELECT * FROM table2;`
                                    - DuckDB has an inutitive syntax to create List/Struct/Map and Array types. Create complex types using intuitive syntax. List: `SELECT [1, 2, 3] AS my_list;`, Struct: `{{'a': 1, 'b': 'text'}} AS my_struct;`, Map: `MAP([1,2],['one','two']) as my_map;`. All types can also be nested into each other. Array types are fixed size, while list types have variable size. Compared to Structs, MAPs do not need to have the same keys present for each row, but keys can only be of type Integer or Varchar. Example: `CREATE TABLE example (my_list INTEGER[], my_struct STRUCT(a INTEGER, b TEXT), my_map MAP(INTEGER, VARCHAR),  my_array INTEGER[3], my_nested_struct STRUCT(a INTEGER, b Integer[3]));`
                                    - DuckDB has an inutive syntax to access struct fields using dot notation (.) or brackets ([]) with the field name. Maps fields can be accessed by brackets ([]).
                                    - DuckDB's way of converting between text and timestamps, and extract date parts. Current date as 'YYYY-MM-DD': `SELECT strftime(NOW(), '%Y-%m-%d');` String to timestamp: `SELECT strptime('2023-07-23', '%Y-%m-%d')::TIMESTAMP;`, Extract Year from date: `SELECT EXTRACT(YEAR FROM DATE '2023-07-23');`
                                    - Column Aliases in WHERE/GROUP BY/HAVING: You can use column aliases defined in the SELECT clause within the WHERE, GROUP BY, and HAVING clauses. E.g.: `SELECT a + b AS total FROM my_table WHERE total > 10 GROUP BY total HAVING total < 20;`
                                    - DuckDB allows generating lists using expressions similar to Python list comprehensions. E.g. `SELECT [x*2 FOR x IN [1, 2, 3]];` Returns [2, 4, 6].
                                    - DuckDB allows chaining multiple function calls together using the dot (.) operator. E.g.: `SELECT 'DuckDB'.replace('Duck', 'Goose').upper(); -- Returns 'GOOSEDB';`
                                    - DuckDB has a JSON data type. It supports selecting fields from the JSON with a JSON-Path expression using the arrow operator, -> (returns JSON) or ->> (returns text) with JSONPath expressions. For example: `SELECT data->'$.user.id' AS user_id, data->>'$.event_type' AS event_type FROM events;`
                                    - DuckDB has built-in functions for regex regexp_matches(column, regex), regexp_replace(column, regex), and regexp_extract(column, regex).
                                    - DuckDB has a way to quickly get a subset of your data with `SELECT * FROM large_table USING SAMPLE 10%;`
                                    I will provide you input/output examples and sometimes instructions. 
                                    Please return **only** the DuckDB sql macro code and nothing else. Put the DuckDB sql macro in the quoted block: 
                                       ```sql
                                        CREATE OR REPLACE MACRO string_transformation(a) AS (
                                             SELECT ...
                                        ```
                                       """},
                                    {"role": "user", "content": f"""Instructions: {{instruction}}, Examples: {{examples}}"""}],

            "ENTITY_MATCHING": [{"role": "user", "content": """You are a DuckDB SQL expert. I have an entity matching task to solve. I have pairs of rows and I want you to find a python program that checks if they match with each other. 
                    Please try to match using substring and regex preferably. 
                    First consider using Jaccard, levenshtein, cosine similarity or any other edit distance function to solve the problem. 
                    Try to define a low threshold so that the generated function is **generalizable**.
                    Note that there can be missing values in some columns, and you can skip them for matching. All columns are connected by the symbol ^ in the input string.
                    Please do not train any machine learning classifier.
                    You can try to choose appropriate distance function with revevant columns based on the column meaning.
                    
                    You will have to use the CREATE MACRO statement from DuckDB, following is an example usage:\
                    -- create a macro with a common table expression \
                    -- (parameter names get priority over column names: disambiguate using the table name) \
                    CREATE or REPLACE MACRO string_transformation(a) AS (WITH cte AS (SELECT 1 AS a) SELECT cte.a + a FROM cte); \
                    Please keep the name string_transformation fixed and only generate the expression in the brackets after CREATE OR REPLACE AS (). \
                    Make sure to only use DuckDB SQL to solve the task, no Python udfs or anything like that. \
                    You can for example use DuckDBs regex function as part of the program. \
                    Name	Description
                    regexp_extract_all(string, regex[, group = 0])	Split the string along the regex and extract all occurrences of group. \
                    regexp_extract(string, pattern , name_list);	If string contains the regexp pattern, returns the capturing groups as a struct with corresponding names from name_list. \
                    regexp_extract(string, pattern [, idx]);	If string contains the regexp pattern, returns the capturing group specified by optional parameter idx. \
                    regexp_full_match(string, regex)	Returns true if the entire string matches the regex. \
                    regexp_matches(string, pattern)	Returns true if string contains the regexp pattern, false otherwise. \
                    regexp_replace(string, pattern, replacement);	If string contains the regexp pattern, replaces the matching part with replacement. \
                    regexp_split_to_array(string, regex)	Alias of string_split_regex. Splits the string along the regex. \
                    regexp_split_to_table(string, regex)	Splits the string along the regex and returns a row for each part. \
                    When use backslash symbol, please use only single backslash instead of two, so the query can be executed. \
                    If using regex, please come up with correct pattern and make sure the extraction will not be empty \
                    Here are some DuckDB SQL syntax specifics you should be aware of:
                    - DuckDB use double quotes (") for identifiers that contain spaces or special characters, or to force case-sensitivity and single quotes (') to define string literals
                    - DuckDB can query CSV, Parquet, and JSON directly without loading them first, e.g. `SELECT * FROM 'data.csv';`
                    - DuckDB supports CREATE TABLE AS (CTAS): `CREATE TABLE new_table AS SELECT * FROM old_table;`
                    - DuckDB queries can start with FROM, and optionally omit SELECT *, e.g. `FROM my_table WHERE condition;` is equivalent to `SELECT * FROM my_table WHERE condition;`
                    - DuckDB allows you to use SELECT without a FROM clause to generate a single row of results or to work with expressions directly, e.g. `SELECT 1 + 1 AS result;`
                    - DuckDB supports attaching multiple databases, unsing the ATTACH statement: `ATTACH 'my_database.duckdb' AS mydb;`. Tables within attached databases can be accessed using the dot notation (.), e.g. `SELECT * FROM mydb.table_name syntax`. The default databases doesn't require the do notation to access tables. The default database can be changed with the USE statement, e.g. `USE my_db;`.
                    - DuckDB is generally more lenient with implicit type conversions (e.g. `SELECT '42' + 1;` - Implicit cast, result is 43), but you can always be explicit using `::`, e.g. `SELECT '42'::INTEGER + 1;`
                    - DuckDB can extract parts of strings and lists using [start:end] or [start:end:step] syntax. Indexes start at 1. String slicing: `SELECT 'DuckDB'[1:4];`. Array/List slicing: `SELECT [1, 2, 3, 4][1:3];`
                    - DuckDB has a powerful way to select or transform multiple columns using patterns or functions. You can select columns matching a pattern: `SELECT COLUMNS('sales_.*') FROM sales_data;` or transform multiple columns with a function: `SELECT AVG(COLUMNS('sales_.*')) FROM sales_data;`
                    - DuckDB an easy way to include/exclude or modify columns when selecting all: e.g. Exclude: `SELECT * EXCLUDE (sensitive_data) FROM users;` Replace: `SELECT * REPLACE (UPPER(name) AS name) FROM users;`
                    - DuckDB has a shorthand for grouping/ordering by all non-aggregated/all columns. e.g `SELECT category, SUM(sales) FROM sales_data GROUP BY ALL;` and `SELECT * FROM my_table ORDER BY ALL;`
                    - DuckDB can combine tables by matching column names, not just their positions using UNION BY NAME. E.g. `SELECT * FROM table1 UNION BY NAME SELECT * FROM table2;`
                    - DuckDB has an inutitive syntax to create List/Struct/Map and Array types. Create complex types using intuitive syntax. List: `SELECT [1, 2, 3] AS my_list;`, Struct: `{{'a': 1, 'b': 'text'}} AS my_struct;`, Map: `MAP([1,2],['one','two']) as my_map;`. All types can also be nested into each other. Array types are fixed size, while list types have variable size. Compared to Structs, MAPs do not need to have the same keys present for each row, but keys can only be of type Integer or Varchar. Example: `CREATE TABLE example (my_list INTEGER[], my_struct STRUCT(a INTEGER, b TEXT), my_map MAP(INTEGER, VARCHAR),  my_array INTEGER[3], my_nested_struct STRUCT(a INTEGER, b Integer[3]));`
                    - DuckDB has an inutive syntax to access struct fields using dot notation (.) or brackets ([]) with the field name. Maps fields can be accessed by brackets ([]).
                    - DuckDB's way of converting between text and timestamps, and extract date parts. Current date as 'YYYY-MM-DD': `SELECT strftime(NOW(), '%Y-%m-%d');` String to timestamp: `SELECT strptime('2023-07-23', '%Y-%m-%d')::TIMESTAMP;`, Extract Year from date: `SELECT EXTRACT(YEAR FROM DATE '2023-07-23');`
                    - Column Aliases in WHERE/GROUP BY/HAVING: You can use column aliases defined in the SELECT clause within the WHERE, GROUP BY, and HAVING clauses. E.g.: `SELECT a + b AS total FROM my_table WHERE total > 10 GROUP BY total HAVING total < 20;`
                    - DuckDB allows generating lists using expressions similar to Python list comprehensions. E.g. `SELECT [x*2 FOR x IN [1, 2, 3]];` Returns [2, 4, 6].
                    - DuckDB allows chaining multiple function calls together using the dot (.) operator. E.g.: `SELECT 'DuckDB'.replace('Duck', 'Goose').upper(); -- Returns 'GOOSEDB';`
                    - DuckDB has a JSON data type. It supports selecting fields from the JSON with a JSON-Path expression using the arrow operator, -> (returns JSON) or ->> (returns text) with JSONPath expressions. For example: `SELECT data->'$.user.id' AS user_id, data->>'$.event_type' AS event_type FROM events;`
                    - DuckDB has built-in functions for regex regexp_matches(column, regex), regexp_replace(column, regex), and regexp_extract(column, regex).
                    - DuckDB has a way to quickly get a subset of your data with `SELECT * FROM large_table USING SAMPLE 10%;`
                    I will provide you input/output examples and sometimes instructions. 
                    Please return **only** the DuckDB sql macro code and nothing else. Put the DuckDB sql macro in the quoted block: 
                    ```sql
                    CREATE OR REPLACE MACRO input_output_converter(a) AS (
                            SELECT ...
                    ```
                    Please return only the DuckDB sql macro and nothing else. Include any imports. Please do **not** provide any comments. 
                    After generating the function string, please add escape symbol tab '\t' to format the code properly with indents like shown in the example."""},\
                        {"role": "user", "content": f"""Instructions: {{instruction:}}, Examples: {{examples:}}"""}]
}

def get_prompts_set(lang, use_data_router=True):
    if lang == "python" and use_data_router:
        return PYTHON_PROMPTS_ROUTE_DATA
    elif lang == "python" and not use_data_router:
        return PYTHON_PROMPTS
    elif lang == "sql" and use_data_router:
        return SQL_PROMPTS_ROUTE_DATA
    elif lang == "sql" and not use_data_router:
        return SQL_PROMPTS
    else:
        raise NotImplementedError

class PromptTemplate:
    def __init__(self, prompt) -> None:
        self.prompt = prompt

    def execute(self):
        pass

    def reset(self):
        self.inital_prompt = ""
        self.message_history = []

    def assign_new_prompt(self, new_prompt: List) -> None:
        self.prompt = new_prompt

    def add_prompt_incremental(self, prompt_to_add: Dict) -> None:
        self.prompt.append(prompt_to_add) 






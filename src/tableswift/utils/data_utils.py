########################################
# adapted from: https://github.com/HazyResearch/fm_data_tasks/blob/updates/fm_data_tasks/utils/data_utils.py 
########################################

"""Data utils."""
import os
import copy
import logging
from functools import partial
from pathlib import Path
from typing import Dict, List

import pandas as pd

import utils.contants as constants
from promptsTemplate import *

logger = logging.getLogger(__name__)


ERROR_DETECTION_SPELLING_INSTR =  f"""I have a table with adult data, now I will provide rows of records with the column name: {{column_name}}, please write an appropriate python program that checks if there are any spelling errors. Return "yes" if there is spelling and "no" if there is none."""


def sample_train_data(train: pd.DataFrame, n_rows: int) -> pd.DataFrame:
    """
    Sample train data.

    Used when random sampling points for prompt.
    """
    res = train.sample(n_rows)
    return res

def sample_train_data_stratified(train: pd.DataFrame, n_rows: int) -> pd.DataFrame:
    """
    Sample train data while attempting to maintain the distribution of 'label_str'.
    
    Parameters:
    - train: The training dataset as a pandas DataFrame.
    - n_rows: The total number of rows to sample.
    
    Returns:
    - A pandas DataFrame containing the sampled data.
    """
    # Calculate the number of samples per label based on their distribution in the dataset
    n_labels = train['label_str'].nunique()
    samples_per_label = max(n_rows // n_labels, 1)  # Ensure at least 1 sample per label
    print("Using stratefied sampling! number of samplers per label: ", samples_per_label)
    
    # Adjust n_rows to fit the actual number of samples we can get
    adjusted_n_rows = samples_per_label * n_labels
    
    # Sample from each label
    def sample_from_group(group):
        return group.sample(min(len(group), samples_per_label), replace=True)

    # Group by 'label_str' and apply sampling
    res = train.groupby('label_str', group_keys=False).apply(sample_from_group)
    
    # If adjusted_n_rows < n_rows, sample additional rows randomly to fill up to n_rows
    if len(res) < n_rows:
        additional_samples = n_rows - len(res)
        additional_rows = train.sample(additional_samples)
        res = pd.concat([res, additional_rows], ignore_index=False)
    
    return res

def serialize_row(
    row: pd.core.series.Series,
    column_map: Dict[str, str],
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn structured row into string."""
    res = []
    for c_og, c_map in column_map.items():
        if str(row[c_og]) == "nan":
            row[c_og] = nan_tok
        else:
            row[c_og] = f"{row[c_og]}".strip()
        res.append(f"{c_map}: {row[c_og]}".lstrip())
    if len(sep_tok) > 0 and sep_tok != ".":
        sep_tok = f" {sep_tok}"
    return f"{sep_tok} ".join(res)


def serialize_match_pair(
    row: pd.core.series.Series,
    column_mapA: Dict[str, str],
    column_mapB: Dict[str, str],
    add_instruction: bool,
    instruction: str,
    suffix: str,
    prod_name: str,
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn structured pair of entities into string for matching."""
    res = (
        f"{prod_name} A is {serialize_row(row, column_mapA, sep_tok, nan_tok)}."
        f" {prod_name} B is {serialize_row(row, column_mapB, sep_tok, nan_tok)}."
        f"{suffix} "
    )
    if add_instruction:
        res = f"{instruction} {res}"
    return res


def serialize_imputation(
    row: pd.core.series.Series,
    column_map: Dict[str, str],
    impute_col: str,
    add_instruction: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn single entity into string for imputation."""
    assert impute_col not in column_map, f"{impute_col} cannot be in column map"
    # Rename to avoid passing white spaced sep token to serialize_row
    sep_tok_ws = sep_tok
    if len(sep_tok) > 0 and sep_tok != ".":
        sep_tok_ws = f" {sep_tok}"
    res = f"{serialize_row(row, column_map, sep_tok, nan_tok)}{sep_tok_ws}{suffix} "
    if add_instruction:
        res = f"{instruction} {res}"
    return res


def serialize_error_detection_spelling(
    row: pd.core.series.Series,
    add_instruction: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn single cell into string for error detection."""
    column_map = {row["col_name"]: row["col_name"]}
    res = f"Is there a x spelling error in {serialize_row(row, column_map, sep_tok, nan_tok)}{suffix} "
    if add_instruction:
        res = f"{instruction} {res}"
    return res


def serialize_error_detection(
    row: pd.core.series.Series,
    add_prefix: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn single cell into string for error detection."""
    column_map = {
        c: c
        for c in row.index
        if str(c) not in ["Unnamed: 0", "text", "col_name", "label_str", "is_clean"]
    }
    entire_row = serialize_row(row, column_map, sep_tok, nan_tok)
    column_map = {row["col_name"]: row["col_name"]}
    res = f"{entire_row}\n\nIs there an error in {serialize_row(row, column_map, sep_tok, nan_tok)}{suffix} "
    if add_prefix:
        res = f"{instruction} {res}"
    return res


def serialize_schema_match(
    row: pd.core.series.Series,
    add_prefix: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> str:
    """Turn single cell into string for schema matching."""
    res = f"A is {row['left']}. B is {row['right']}. {suffix} "
    if add_prefix:
        res = f"{instruction}\n\n{res}"
    return res

def serialize_row_simple(row, sep_tok="^", nan_tok='nan'):
    """
    Serialize a DataFrame row into a string.

    Parameters:
    - row: A Pandas Series representing a row in a DataFrame.
    - separator: A string separator used between each value in the row. Defaults to ', '.
    - nan_replacement: A string used to replace NaN values. Defaults to 'N/A'.

    Returns:
    - A string representing the serialized row.
    """
    # Convert each value in the row to string, replace NaN values with the specified replacement
    return sep_tok.join([str(v) if pd.notnull(v) else nan_tok for v in row])


def serialize_row_for_merge(row, prefix, sep_tok, nan_tok):
    # Filter and serialize columns for each part of the merged DataFrame
    filtered_row = row.filter(regex=f'_{prefix}$').rename(lambda x: x[:-2])
    return serialize_row_simple(filtered_row, sep_tok, nan_tok)


def read_blocked_pairs_simple(split_path: str, tableA: pd.DataFrame, tableB: pd.DataFrame, sep_tok='; ', nan_tok='N/A') -> pd.DataFrame:
    labels = pd.read_csv(split_path)
    # Merge the labels with tableA and tableB
    mergedA = pd.merge(labels, tableA, right_on="id", left_on="ltable_id")
    merged = pd.merge(
        mergedA,
        tableB,
        right_on="id",
        left_on="rtable_id",
        suffixes=("_A", "_B"),
    )

    # Format the "text" column by combining serialized parts from tableA and tableB
    merged["text"] = merged.apply(
        lambda row: f"A: {serialize_row_for_merge(row, 'A', sep_tok, nan_tok)}{sep_tok}B: {serialize_row_for_merge(row, 'B', sep_tok, nan_tok)}",
        axis=1,
    )
    # Create the "label_str" column based on the "label" value
    merged["label_str"] = merged["label"].apply(lambda x: "Yes" if x == 1 else "No")

    # Return only the necessary columns
    return merged[["text", "label_str"]]



def read_blocked_pairs(
    split_path: str,
    tableA: pd.DataFrame,
    tableB: pd.DataFrame,
    cols_to_drop: List[str],
    col_renaming: Dict[str, str],
    add_instruction: bool,
    instruction: str,
    suffix: str,
    prod_name: str,
    sep_tok: str,
    nan_tok: str,
) -> pd.DataFrame:
    """Read in pre-blocked pairs with T/F match labels."""
    for c in cols_to_drop:
        tableA = tableA.drop(c, axis=1, inplace=False)
        tableB = tableB.drop(c, axis=1, inplace=False)
    if len(col_renaming) > 0:
        tableA = tableA.rename(columns=col_renaming, inplace=False)
        tableB = tableB.rename(columns=col_renaming, inplace=False)

    column_mapA = {f"{c}_A": c for c in tableA.columns if c != "id"}
    column_mapB = {f"{c}_B": c for c in tableB.columns if c != "id"}

    labels = pd.read_csv(split_path)

    mergedA = pd.merge(labels, tableA, right_on="id", left_on="ltable_id")
    merged = pd.merge(
        mergedA,
        tableB,
        right_on="id",
        left_on="rtable_id",
        suffixes=("_A", "_B"),
    )

    merged["text"] = merged.apply(
        lambda row: serialize_match_pair(
            row,
            column_mapA,
            column_mapB,
            add_instruction,
            instruction,
            suffix,
            prod_name,
            sep_tok,
            nan_tok,
        ),
        axis=1,
    )
    merged["label_str"] = merged.apply(
        lambda row: "Yes\n" if row["label"] == 1 else "No\n", axis=1
    )
    return merged


def read_imputation_single_simple(
    split_path: str,
    impute_col: str,
    sep_tok: str,
    nan_tok: str,
) -> pd.DataFrame:
    """Read in table and create label impute col."""
    table = pd.read_csv(split_path)
    column_map = {c: c for c in table.columns if c != "id" and c != impute_col}
    table["text"] = table.apply(
        lambda row: serialize_row(row=row, column_map=column_map, sep_tok=sep_tok, nan_tok=nan_tok),
        axis=1,
    )
    table["label_str"] = table[impute_col].apply(lambda x: f"{x}\n")
    return table


def read_imputation_single(
    split_path: str,
    impute_col: str,
    cols_to_drop: List[str],
    col_renaming: Dict[str, str],
    add_instruction: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> pd.DataFrame:
    """Read in table and create label impute col."""
    table = pd.read_csv(split_path)
    for c in cols_to_drop:
        table = table.drop(c, axis=1, inplace=False)
    if len(col_renaming) > 0:
        table = table.rename(columns=col_renaming, inplace=False)
    column_map = {c: c for c in table.columns if c != "id" and c != impute_col}

    table["text"] = table.apply(
        lambda row: serialize_imputation(
            row,
            column_map,
            impute_col,
            add_instruction,
            instruction,
            suffix,
            sep_tok,
            nan_tok,
        ),
        axis=1,
    )
    table["label_str"] = table[impute_col].apply(lambda x: f"{x}\n")
    return table


def read_data_transformation_single(
        directory_path: str,
        cols_to_drop: List[str],
        col_renaming: Dict[str, str],
        add_instruction: bool,
        instruction: str,
        suffix: str,
        sep_tok: str = '\t',
        nan_tok: str = 'NaN',
    ) -> List[pd.DataFrame]:
        dataframes = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory_path, filename)
                df = pd.read_csv(file_path, sep=sep_tok, names=['Time', 'Hours'])
                # Apply any processing here, similar to your read_imputation_single function
                for c in cols_to_drop:
                    df.drop(c, axis=1, inplace=True)
                if col_renaming:
                    df.rename(columns=col_renaming, inplace=True)
                # Add any specific processing here, you might need to adjust it based on your actual needs
                dataframes.append(df)
        return dataframes


def read_error_detection_single(
    split_path: str,
    table: pd.DataFrame,
    cols_to_drop: List[str],
    col_renaming: Dict[str, str],
    add_instruction: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
    spelling: bool,
) -> pd.DataFrame:
    """Read in table and create label impute col."""
    for c in cols_to_drop:
        table = table.drop(c, axis=1, inplace=False)
    if len(col_renaming) > 0:
        table = table.rename(columns=col_renaming, inplace=False)
    # row_id, col_name, is_clean
    labels = pd.read_csv(split_path)

    if spelling:
        merged = pd.merge(labels, table, left_on="row_id", right_index=True)
        merged["text"] = merged.apply(
            lambda row: serialize_error_detection_spelling(
                row,
                add_instruction,
                instruction,
                suffix,
                sep_tok,
                nan_tok,
            ),
            axis=1,
        )
    else:
        merged = table
        merged["text"] = merged.apply(
            lambda row: serialize_error_detection(
                row,
                add_instruction,
                instruction,
                suffix,
                sep_tok,
                nan_tok,
            ),
            axis=1,
        )

    merged["label_str"] = merged.apply(
        lambda row: "No\n" if row["is_clean"] == 1 else "Yes\n", axis=1
    )
    return merged

def read_error_detection_single_simple(
    split_path: str
) -> List[pd.DataFrame]:
    """Read in tables and return a list of dataframes."""
    dataframes = []
    instructions = []
    # List all files in the folder
    for file_name in os.listdir(split_path):
        # Check if the file is a CSV
        if file_name.endswith('.csv'):
            # Extract column name from the file name
            column_name = file_name.split("_")[2].split(".csv")[0]
            
            # Read the CSV file into a DataFrame
            file_path = os.path.join(split_path, file_name)
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower()
            # Add the 'column_name' to the DataFrame
            df['text'] = df[column_name]
            
            # Rename 'is_clean' to 'label_str'
            df['label_str'] = df['is_clean'].map({1: 'no', 0: 'yes'})

            
            df.drop('is_clean', axis=1, inplace=True)
            
            # Add the DataFrame to the list
            dataframes.append(df)
            instruction = copy.deepcopy(ERROR_DETECTION_SPELLING_INSTR)
            instructions.append(instruction.format(column_name=column_name))
    return dataframes, instructions

    

def read_schema_match_single(
    split_path: str,
    table: pd.DataFrame,
    cols_to_drop: List[str],
    col_renaming: Dict[str, str],
    add_instruction: bool,
    instruction: str,
    suffix: str,
    sep_tok: str,
    nan_tok: str,
) -> pd.DataFrame:
    """Read in table and create label impute col."""
    file = pd.read_csv(split_path)
    for c in cols_to_drop:
        file = file.drop(c, axis=1, inplace=False)
    if len(col_renaming) > 0:
        file = file.rename(columns=col_renaming, inplace=False)
    # row_id, col_name, is_clean
    # labels = pd.read_csv(split_path)
    # merged = pd.merge(labels, table, left_on="Unnamed: 0", right_index=True)
    file["text"] = file.apply(
        lambda row: serialize_schema_match(
            row,
            add_instruction,
            instruction,
            suffix,
            sep_tok,
            nan_tok,
        ),
        axis=1,
    )
    file["label_str"] = file.apply(
        lambda row: "No\n" if row["label"] == 0 else "Yes\n", axis=1
    )
    return file


def read_transformation_data(data_path, k=3) -> List[pd.DataFrame]:
    """ 
    We read the data transformation dataset here. 
    We first check if there are instructions in the beginning of the file.
    We then split the input output examples to train and test.
    We save the data in to a list of dataframes.
    """
    data_files_sep = {"train": [], "test": [], "instructions": []}  # Dictionary to hold train and test dataframes
    
    for filename in os.listdir(data_path):
        # if "semantic" in filename:
        file_path = os.path.join(data_path, filename)
        
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except:
            continue 
        # Determine if the first line is an instruction and remove it if so
        instruction = None
        if lines[0].startswith("//"):
            instruction = lines.pop(0).strip()
        
        # Process the remaining lines into input-output pairs
        input_output_pairs = []
        for line in lines:
            if line.strip():
                line_split = line.strip().split('\t\t')
                line_split = [t for t in line_split if t.strip() and not t == '\t' and not t == '\t\t']
                input_output_pairs.append(line_split)
                if len(line_split) > 2:
                    print(file_path)
        # Create a DataFrame from the pairs
        df = pd.DataFrame(input_output_pairs, columns=["text", "label_str"])
        
        # Split the DataFrame into train and test
        train_df = df.iloc[:k]  # The first k entries are for training
        test_df = df.iloc[k:]   # The rest are for testing
        
        # Append the train and test DataFrames to their respective lists in the dictionary
        data_files_sep["train"].append(train_df)
        data_files_sep["test"].append(test_df)
        data_files_sep["instructions"].append(instruction)
        
    return data_files_sep

def sort_list_pairs(pair1, pair2, pair3):
    # Unpack the pairs into separate lists
    list1a, list1b = pair1
    list2a, list2b = pair2
    list3a, list3b = pair3

    # Determine the sorting order based on the second lists
    sort_order = sorted(range(len(list1b)), key=lambda i: (list1b[i], list2b[i], list3b[i]))

    # Sort each first list based on the determined sort order
    sorted_list1a = [list1a[i] for i in sort_order]
    sorted_list2a = [list2a[i] for i in sort_order]
    sorted_list3a = [list3a[i] for i in sort_order]

    # Sort the second lists to make them identical
    sorted_list1b = sorted(list1b)
    sorted_list2b = sorted(list2b)
    sorted_list3b = sorted(list3b)

    # Return the sorted pairs
    return (sorted_list1a, sorted_list1b), (sorted_list2a, sorted_list2b), (sorted_list3a, sorted_list3b)


def read_raw_data_simple(data_dir: str, sep_tok:str, nan_tok:str, k:int=3):
    data_files_sep = {"test": {}, "train": {}, "validation": {}}
    logger.info(f"Reading data from {data_dir}")
    if data_dir not in constants.DATA2TASK:
        raise ValueError(
            f"{data_dir} not one of {constants.DATA2TASK.keys()}. Make sure to set DATASET_PATH."
        )
    task = constants.DATA2TASK[data_dir]
    data_dir_p = Path(data_dir) 
    if task == "entity_matching":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        tableA_file = data_dir_p / "tableA.csv"
        tableB_file = data_dir_p / "tableB.csv"

        tableA = pd.read_csv(tableA_file)
        tableB = pd.read_csv(tableB_file)
        label_col = "label"
        data_files_sep["train"] = read_blocked_pairs_simple(train_file, sep_tok=sep_tok, nan_tok=nan_tok, tableA=tableA, tableB=tableB)
        # Read validation
        if valid_file.exists():
            data_files_sep["validation"] = read_blocked_pairs_simple(valid_file,sep_tok=sep_tok, nan_tok=nan_tok, tableA=tableA, tableB=tableB)
        # Read test
        if test_file.exists():
            data_files_sep["test"] = read_blocked_pairs_simple(test_file,sep_tok=sep_tok, nan_tok=nan_tok, tableA=tableA, tableB=tableB)
    elif task == "data_imputation":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        label_col = constants.IMPUTE_COLS[data_dir]
        data_files_sep["train"] = read_imputation_single_simple(split_path=valid_file, impute_col=label_col, sep_tok=sep_tok, nan_tok=nan_tok)
        # Read validation
        if valid_file.exists():
            data_files_sep["validation"] = read_imputation_single_simple(split_path=valid_file, impute_col=label_col, sep_tok=sep_tok, nan_tok=nan_tok)
        # Read test
        if test_file.exists():
            data_files_sep["test"] = read_imputation_single_simple(split_path=test_file, impute_col=label_col, sep_tok=sep_tok, nan_tok=nan_tok)
    
    elif task == "error_detection_spelling":
        train_path = data_dir_p / "train_splits_single"
        valid_path = data_dir_p / "valid_splits_single"
        test_path = data_dir_p / "test_splits_single"
        print(train_path)
        label_col = "label_str"
        train_dfs, instructions_train = read_error_detection_single_simple(train_path)
        valid_dfs, instructions_valid = read_error_detection_single_simple(valid_path)
        test_dfs, instructions_test = read_error_detection_single_simple(test_path)
        
        (train_dfs, instructions_train), (valid_dfs, instructions_valid), (test_dfs, instructions_test) = \
            sort_list_pairs((train_dfs, instructions_train), (valid_dfs, instructions_valid), (test_dfs, instructions_test))
        data_files_sep["train"] = train_dfs
        data_files_sep["valid"] = valid_dfs
        data_files_sep["test"] = test_dfs
        data_files_sep["instructions"] = instructions_train
        if instructions_train == instructions_test == instructions_valid:
            print("correct sorted")

    elif task == "data_transformation":
        data_files_sep = read_transformation_data(data_dir_p, k)
        label_col = "label_str"
    else:
        raise ValueError(f"Task {task} not recognized.")
    

    return data_files_sep, label_col


def read_raw_data(
    data_dir: str,
    add_instruction: bool = False,
    task_instruction_idx: int = 0,
    sep_tok: str = ".",
    nan_tok: str = "nan",
    k: int = 3
):
    """Read in data where each directory is unique for a task."""
    data_files_sep = {"test": {}, "train": {}, "validation": {}}
    logger.info(f"Processing {data_dir}")
    if data_dir not in constants.DATA2TASK:
        raise ValueError(
            f"{data_dir} not one of {constants.DATA2TASK.keys()}. Make sure to set DATASET_PATH."
        )
    task = constants.DATA2TASK[data_dir]
    instruction = constants.DATA2INSTRUCT[data_dir]
    suffix = constants.DATA2SUFFIX[data_dir]
    cols_to_drop = constants.DATA2DROPCOLS[data_dir]
    col_renaming = constants.DATA2COLREMAP[data_dir]
    data_dir_p = Path(data_dir)  

    if task == "entity_matching":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        tableA_file = data_dir_p / "tableA.csv"
        tableB_file = data_dir_p / "tableB.csv"

        tableA = pd.read_csv(tableA_file)
        tableB = pd.read_csv(tableB_file)

        label_col = "label"
        read_data_func = partial(
            read_blocked_pairs,
            tableA=tableA,
            tableB=tableB,
            cols_to_drop=cols_to_drop,
            col_renaming=col_renaming,
            add_instruction=add_instruction,
            instruction=instruction,
            suffix=suffix,
            prod_name=constants.MATCH_PROD_NAME[data_dir],
            sep_tok=sep_tok,
            nan_tok=nan_tok,
        )
    elif task == "data_imputation":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        label_col = constants.IMPUTE_COLS[data_dir]
        read_data_func = partial(
            read_imputation_single,
            impute_col=label_col,
            cols_to_drop=cols_to_drop,
            col_renaming=col_renaming,
            add_instruction=add_instruction,
            instruction=instruction,
            suffix=suffix,
            sep_tok=sep_tok,
            nan_tok=nan_tok,
        )
    elif task == "error_detection_spelling":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        table_file = data_dir_p / "table.csv"

        table = pd.read_csv(table_file)
        label_col = "is_clean"
        read_data_func = partial(
            read_error_detection_single,
            table=table,
            cols_to_drop=cols_to_drop,
            col_renaming=col_renaming,
            add_instruction=add_instruction,
            instruction=instruction,
            suffix=suffix,
            sep_tok=sep_tok,
            nan_tok=nan_tok,
            spelling=True,
        )
    elif task == "error_detection":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        table_file = data_dir_p / "table.csv"

        table = pd.read_csv(table_file)
        label_col = "is_clean"
        read_data_func = partial(
            read_error_detection_single,
            table=table,
            cols_to_drop=cols_to_drop,
            col_renaming=col_renaming,
            add_instruction=add_instruction,
            instruction=instruction,
            suffix=suffix,
            sep_tok=sep_tok,
            nan_tok=nan_tok,
            spelling=False,
        )
    elif task == "schema_matching":
        train_file = data_dir_p / "train.csv"
        valid_file = data_dir_p / "valid.csv"
        test_file = data_dir_p / "test.csv"
        table_file = data_dir_p / "table.csv"
        label_col = "label"
        table = pd.read_csv(table_file)
        read_data_func = partial(
            read_schema_match_single,
            table=table,
            cols_to_drop=cols_to_drop,
            col_renaming=col_renaming,
            add_instruction=add_instruction,
            instruction=instruction,
            suffix=suffix,
            sep_tok=sep_tok,
            nan_tok=nan_tok,
        )
    elif task == "data_transformation":
        data_files_sep = read_transformation_data(data_dir_p, k)
        label_col = "label_str"
        return data_files_sep, label_col
    else:
        raise ValueError(f"Task {task} not recognized.")

    data_files_sep["train"] = read_data_func(train_file)
    # Read validation
    if valid_file.exists():
        data_files_sep["validation"] = read_data_func(valid_file)
    # Read test
    if test_file.exists():
        data_files_sep["test"] = read_data_func(test_file)
    return data_files_sep, label_col



def read_data(
    data_dir: str,
    class_balanced: bool = False,
    add_instruction: bool = False,
    task_instruction_idx: int = 0,
    max_train_samples: int = -1,
    max_train_percent: float = -1,
    sep_tok: str = ".",
    nan_tok: str = "nan",
):
    """Read in data where each directory is unique for a task."""
    print(os.environ.get("DATASET_PATH", Path("data/datasets").resolve()))
    
    task = constants.DATA2TASK[data_dir]

    data_files_sep, label_col = read_raw_data_simple(
        data_dir=data_dir,
        sep_tok=sep_tok,
        nan_tok=nan_tok,
    )
    task = constants.DATA2TASK[data_dir]
    # Don't class balance on open ended classificiation tasks
    if class_balanced and task != "data_imputation":
        # Class balance sample the train data
        label_cnts = data_files_sep["train"].groupby(label_col).count()
        sample_per_class = label_cnts.min()["text"]
        logger.info(f"Class balanced: train sample per class: {sample_per_class}")
        data_files_sep["train"] = (
            data_files_sep["train"]
            .groupby(label_col, group_keys=False)
            .apply(lambda x: x.sample(sample_per_class, random_state=42))
        )
    # handle different data formats
    if isinstance(data_files_sep["train"], List):
        shuffled_data_files_sep = []
        for train_df in data_files_sep["train"]:
            shuffled_data_files_sep.append(train_df.sample(frac=1, random_state=42).reset_index(drop=True))
        data_files_sep["train"] = shuffled_data_files_sep
    elif isinstance(data_files_sep["train"], pd.DataFrame):
        # Shuffle train data
        data_files_sep["train"] = (
            data_files_sep["train"].sample(frac=1, random_state=42).reset_index(drop=True)
        )
        if max_train_samples > 0:
            orig_train_len = len(data_files_sep["train"])
            if max_train_samples > 1.0:
                raise ValueError("max_train_samples must be between 0 and 1")
            max_examples = int(max_train_samples * orig_train_len)
            data_files_sep["train"] = data_files_sep["train"].iloc[:max_examples]
            logger.info(
                f"Length of {data_dir} train is "
                f"{data_files_sep['train'].shape[0]} from {orig_train_len}"
            )
    return data_files_sep, task


def deserialize_data(data: pd.DataFrame) -> list:
    sampled_examples = []
    for txt, label in zip(data["text"], data["label_str"]):
        sampled_examples.append({"Input": str(txt).strip(), "Output": label.strip() if label else label})

    return sampled_examples


def sample_data_random(train_data: pd.DataFrame, num_examples: int=3) -> Tuple[list, pd.DataFrame]:
    """Get random examples from train data for demonstration. Return a list of dictionaries"""
    prefix_exs_rows = sample_train_data(train_data, num_examples)
    return deserialize_data(prefix_exs_rows), prefix_exs_rows

def sample_data_stratified(train_data: pd.DataFrame, num_examples: int=3) -> Tuple[list, pd.DataFrame]:
    prefix_exs_rows = sample_train_data_stratified(train_data, num_examples)
    return deserialize_data(prefix_exs_rows), prefix_exs_rows


def read_instruction(data_dir: str) -> str:
    """
    Extracts instruction from a text file. Used for data_imputation and entity_matching

    Parameters:
    - data_dir: The directory to the text file containing the instruction.

    Returns:
    - The instruction extracted from the file.
    """
    file_path = os.path.join(data_dir, "instruction.txt")
    try:
        with open(file_path, 'r') as file:
            instruction = file.read().strip()
            # Remove leading '//' if present
            if instruction.startswith("//"):
                instruction = instruction[2:].strip()
            return instruction
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None




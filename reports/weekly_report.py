import pandas as pd
from datetime import datetime as c_time


def generate_weekly_report(old_file, new_file):
    """
    Generate two separate reports comparing old and new data:
    - New cases (identified by Case Number and Work Type) in the new_file that do not exist in old_file.
    - Cases (by Case Number and Work Type) whose status changed to "Closed."

    Exports two separate CSV files:
    1. New Cases Report
    2. Cases Changed to Closed Report

    Parameters:
        old_file (str): Path to the cleaned "old" dataset (processed by csv_cleanup.py).
        new_file (str): Path to the cleaned "new" dataset (processed by csv_cleanup.py).

    Output:
        Two CSV files are generated with the results.
    """
    # Load both CSV files (input files are already normalized/cleaned)
    df_old_original = pd.read_csv(old_file, dtype=str)
    df_new_original = pd.read_csv(new_file, dtype=str)

    # **Step 1: Ensure Columns Are in the Correct Order**
    # Identify all unique columns across both files
    column_order = sorted(set(df_old_original.columns) | set(df_new_original.columns))

    # Align both DataFrames to have the same set of columns
    df_old = df_old_original.reindex(columns=column_order, fill_value="")
    df_new = df_new_original.reindex(columns=column_order, fill_value="")

    # Specify key columns
    case_column = 'Case Number'
    work_type_column = 'Work Types'
    status_column = 'Statuses'

    # Ensure the required columns exist
    for col in [case_column, work_type_column, status_column]:
        if col not in df_old.columns or col not in df_new.columns:
            raise ValueError(f"Column '{col}' missing in one of the files.")

    ### 2. Find New Cases ###
    # Create a unique identifier for comparison: Case Number + Work Types
    df_old['unique_key'] = df_old[case_column] + '_' + df_old[work_type_column]
    df_new['unique_key'] = df_new[case_column] + '_' + df_new[work_type_column]

    # Locate entries in `new_file` that are not in `old_file` based on the unique_key
    new_cases = df_new[~df_new['unique_key'].isin(df_old['unique_key'])].copy()
    # new_df_columns = [col for col in merged_cases.columns if not col.endswith('_old')]
    df_columns_new_cases = [col for col in df_new_original.columns]
    new_cases = new_cases[df_columns_new_cases]
    new_cases['Change Type'] = 'New Case'  # Tag these rows for clarity
    # new_cases.rename(columns=lambda col: col[:-4] if col.endswith('_new') else col, inplace=True)

    ### 3. Find Cases Changed to "Closed" ###
    # Match old and new files on `Case Number` AND `Work Type`, including all columns
    merged_cases = pd.merge(
        df_old,  # Include all columns from old DataFrame
        df_new,  # Include all columns from new DataFrame
        on=[case_column, work_type_column],  # Use variables instead of hardcoded names
        suffixes=('_old', '_new'),
        how='inner'  # Only include rows that exist in both files
    )

    # Identify rows where status changed from non-Closed to Closed
    changed_to_closed = merged_cases[
        (~merged_cases[status_column + '_old'].str.contains('Closed', na=False, case=False)) &
        (merged_cases[status_column + '_new'].str.contains('Closed', na=False, case=False))
    ].copy()

    # Keep all columns from the new DataFrame (remove _old suffix columns)
    df_columns_changed_to_closed = [col for col in merged_cases.columns if not col.endswith('_old')]
    changed_to_closed = changed_to_closed[df_columns_changed_to_closed]

    # Remove "_new" suffix from all column names in changed_to_closed
    changed_to_closed.rename(columns=lambda col: col[:-4] if col.endswith('_new') else col, inplace=True)

    # Rename the new status column back to original name and add Previous Status
    changed_to_closed.rename(columns={f"{status_column}_new": status_column}, inplace=True)
    changed_to_closed = changed_to_closed[df_new_original.columns]
    # changed_to_closed['Previous Status'] = merged_cases[status_column + '_old']
    changed_to_closed['Change Type'] = 'Changed to Closed'

    ### 4. Export Results to Separate CSV Files ###
    # Generate unique filenames with timestamps
    current_time = c_time.now().strftime("%d%m%y%H%M%S")
    new_cases_file = f"new_cases_report_{current_time}.csv"
    changed_statuses_file = f"closed_cases_report_{current_time}.csv"

    # Remove unique_key from both DataFrames before saving
    if 'unique_key' in new_cases.columns:
        new_cases = new_cases.drop('unique_key', axis=1)
    if 'unique_key' in changed_to_closed.columns:
        changed_to_closed = changed_to_closed.drop('unique_key', axis=1)

    # Save New Cases Report
    new_cases.to_csv(new_cases_file, index=False, quoting=1)
    print(f"New Cases report successfully generated: {new_cases_file}")

    # Save Changed Statuses Report
    changed_to_closed.to_csv(changed_statuses_file, index=False, quoting=1)
    print(f"Changed Statuses report successfully generated: {changed_statuses_file}")
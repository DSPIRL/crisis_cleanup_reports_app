import pandas as pd
from datetime import datetime as c_time


def normalize_disaster_data(input_file, output_file):
    """
    Reads disaster relief data and splits rows with multiple work types into separate rows.
    Each output row will have exactly one work type with its associated status and claimer.

    Parameters:
    input_file (str): Path to original CSV file
    output_file (str): Path to new CSV file created by this script
    """
    # Read the original CSV file you are wanting to effect/use as an input
    df = pd.read_csv(input_file)

    # Initialize lists to store normalized data
    normalized_rows = []

    for _, row in df.iterrows():
        # Split the multiple values
        work_types = str(row['Work Types']).split('|') if pd.notna(row['Work Types']) else []
        statuses = str(row['Statuses']).split('|') if pd.notna(row['Statuses']) else []
        claimed_by = str(row['Claimed By']).split('|') if pd.notna(row['Claimed By']) else []

        # Ensure claimed_by list is as long as work_types by padding with None
        claimed_by.extend([None] * (len(work_types) - len(claimed_by)))

        # Create a new row for each work type
        for i, work_type in enumerate(work_types):
            new_row = row.copy()
            new_row['Work Types'] = work_type.strip()
            new_row['Statuses'] = statuses[i].strip() if i < len(statuses) else None
            new_row['Claimed By'] = claimed_by[i].strip() if claimed_by[i] else None

            normalized_rows.append(new_row)

    # Create a new DataFrame from the normalized rows
    normalized_df = pd.DataFrame(normalized_rows)

    # Sort by Case Number and Work Types for organization
    normalized_df = normalized_df.sort_values(['Case Number', 'Work Types'])

    # Save to CSV
    normalized_df.to_csv(output_file, index=False)

    # Print summary statistics
    # print(f"\nNormalization complete. Summary:")
    # print(f"Original rows: {len(df)}")
    # print(f"Normalized rows: {len(normalized_df)}")
    # print("\nWork Types distribution:")
    # print(normalized_df['Work Types'].value_counts())
    # print("\nStatus distribution:")
    # print(normalized_df['Statuses'].value_counts())
    # print("\nClaimer distribution:")
    # print(normalized_df['Claimed By'].value_counts())

    return normalized_df


# DOING THE THING
if __name__ == "__main__":
    # Setup input file
    input_file = "input_data.csv"

    # Get current time in DDMMYYHHMMSS format
    current_time = c_time.now()
    formatted_time = current_time.strftime("%m%d%y%H%M%S")

    # Setup output file
    output_file = f"output_data_{formatted_time}.csv"
    normalized_df = normalize_disaster_data(input_file, output_file)

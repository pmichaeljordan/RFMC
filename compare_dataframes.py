import os
import pandas as pd

def load_previous_csv(output_folder):
    csv_files = [f for f in os.listdir(output_folder) if f.endswith('.csv')]
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_folder, x)))
    
    if len(csv_files) < 2:
        print("Not enough CSV files to compare.")
        return None

    previous_csv = csv_files[-2]
    return pd.read_csv(os.path.join(output_folder, previous_csv))

def compare_dataframes(df1, df2):
    comparison = df1.merge(df2, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge'])
    return comparison

def save_comparison_to_csv(comparison, output_folder, file_name):
    os.makedirs(output_folder, exist_ok=True)
    comparison.to_csv(os.path.join(output_folder, file_name), index=False)

if __name__ == "__main__":
    output_folder = 'outputriders'
    previous_df = load_previous_csv(output_folder)

    if previous_df is not None:
        from rfmc_to_google_rev2 import riders_df
        comparison = compare_dataframes(riders_df, previous_df)
        save_comparison_to_csv(comparison, output_folder, 'differences.csv')

from pathlib import Path
import pandas as pd

raw_root = Path("pipeline_data/raw")

date_folders = sorted(
    [folder for folder in raw_root.iterdir() if folder.is_dir()],
    reverse=True
)

if not date_folders:
    raise FileNotFoundError("No dated raw-data folder found.")

latest_folder = date_folders[0]

print(f"\nInspecting folder: {latest_folder}\n")

for file_path in latest_folder.glob("*.csv"):
    df = pd.read_csv(file_path)

    print("=" * 70)
    print(f"FILE: {file_path.name}")
    print(f"ROWS: {len(df):,}")
    print(f"COLUMNS: {len(df.columns)}")
    print(f"DUPLICATE ROWS: {df.duplicated().sum():,}")

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    print("\nDATA TYPES:")
    print(df.dtypes)

    print("\nMISSING VALUES:")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    print("\nFIRST 3 ROWS:")
    print(df.head(3))
    print()
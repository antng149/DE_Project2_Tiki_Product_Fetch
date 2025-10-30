import pandas as pd
import numpy as np

# 1️⃣ Load the CSV
df = pd.read_csv("products-0-200000(in).csv", usecols=["id"])

# 2️⃣ Quick info check
print("Total rows in CSV:", len(df))
print("Blank or missing IDs:", df["id"].isna().sum())
print("Duplicate IDs:", df["id"].duplicated().sum())

# 3️⃣ Clean the IDs
ids = df["id"].dropna()          # remove blank values
ids = ids.astype("int64")        # make sure they’re integers
ids = ids.astype(str)            # convert to string for saving
ids = ids.drop_duplicates()      # remove duplicates

print("Cleaned IDs:", len(ids))

# 4️⃣ Save all IDs
ids.to_csv("product_ids.txt", index=False, header=False)
print("Saved all cleaned IDs to product_ids.txt")

# 5️⃣ Split into 4 parts for your workers
parts = np.array_split(ids, 4)
names = ["ids_A1.txt", "ids_A2.txt", "ids_B1.txt", "ids_B2.txt"]

for name, part in zip(names, parts):
    part.to_csv(name, index=False, header=False)
    print(f"Saved {name} with {len(part)} IDs")

print("All 4 ID files are ready for A1, A2, B1, B2.")
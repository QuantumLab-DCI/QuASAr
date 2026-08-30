import os
from itertools import product

import pandas as pd

from app.core.feature_model import (
    EXCLUDES,
    MANDATORY,
    REQUIRES,
    build_air_quality_feature_model,
)

# --- Configuration ---
CONFIGURATIONS_CSV_PATH = "data/configurations.csv"
OLD_DATASET_PATH = "dataset.csv"
NEW_DATASET_PATH = "data/dataset.csv"
# ---------------------

def get_feature_name(feature_string):
    """Remove the canonical enabled or disabled state from a feature token."""
    return str(feature_string).replace(" enabled", "").replace(" disabled", "")

def _is_valid_configuration(feature_model, configuration):
    for feature in feature_model.features:
        parent_enabled = configuration[feature.key]
        hierarchical_children = []
        xor_children = []
        or_children = []
        for child_key, relationship_type in feature.relationships:
            child_enabled = configuration[child_key]
            if relationship_type not in {REQUIRES, EXCLUDES}:
                hierarchical_children.append(child_key)
            if relationship_type == MANDATORY and parent_enabled and not child_enabled:
                return False
            if relationship_type == "XOR":
                xor_children.append(child_key)
            elif relationship_type == "OR":
                or_children.append(child_key)
            elif relationship_type == REQUIRES and parent_enabled and not child_enabled:
                return False
            elif relationship_type == EXCLUDES and parent_enabled and child_enabled:
                return False
        if not parent_enabled and any(configuration[key] for key in hierarchical_children):
            return False
        if parent_enabled and xor_children:
            if sum(configuration[key] for key in xor_children) != 1:
                return False
        if parent_enabled and or_children:
            if not any(configuration[key] for key in or_children):
                return False
    return True


def create_configuration_template():
    """Enumerate valid configurations from the active feature-model constraints."""
    feature_model = build_air_quality_feature_model()
    feature_keys = [
        feature.key for feature in feature_model.features
        if feature.key != "air_quality_manager"
    ]
    os.makedirs(os.path.dirname(CONFIGURATIONS_CSV_PATH), exist_ok=True)
    rows = []
    for states in product((False, True), repeat=len(feature_keys)):
        configuration = dict(zip(feature_keys, states))
        configuration["air_quality_manager"] = True
        if _is_valid_configuration(feature_model, configuration):
            rows.append([
                f"{feature_key} {'enabled' if configuration[feature_key] else 'disabled'}"
                for feature_key in feature_keys
            ])
    pd.DataFrame(rows).to_csv(CONFIGURATIONS_CSV_PATH, index=False, header=False)
    print(
        f"1. Generated {len(rows)} valid configurations at "
        f"{CONFIGURATIONS_CSV_PATH}."
    )

def create_mapped_dataset():
    """
    Take labeled data from the old 'dataset.csv', map it to the new
    data/configurations.csv structure, and save a new data/dataset.csv.
    """
    if not os.path.exists(CONFIGURATIONS_CSV_PATH):
        print(f"ERROR: {CONFIGURATIONS_CSV_PATH} was not found. Run step 1 first.")
        return

    if not os.path.exists(OLD_DATASET_PATH):
        print(f"ERROR: {OLD_DATASET_PATH} was not found in the working directory.")
        print("Place the previously labeled dataset beside this script before mapping it.")
        return

    print(f"2. Reading the canonical structure from {CONFIGURATIONS_CSV_PATH}.")

    # 1. Get the feature template from the new structure
    new_template = pd.read_csv(CONFIGURATIONS_CSV_PATH, header=None, nrows=1)
    master_feature_list = [get_feature_name(column) for column in new_template.iloc[0]]
    print(f"   Detected {len(master_feature_list)} features.")

    print(f"3. Reading legacy labeled data from {OLD_DATASET_PATH}.")

    # 2. Read the old labeled data
    old_dataset = pd.read_csv(OLD_DATASET_PATH, header=0)

    # Get the old feature names from the header
    old_feature_list = old_dataset.columns[:-1].tolist()
    label_column = old_dataset.columns[-1]

    new_dataset_rows = []

    print(f"4. Mapping {len(old_dataset)} legacy rows to the canonical structure.")

    # 3. Iterate over each old data row (for example, the 8 rows)
    for _index, old_row in old_dataset.iterrows():
        new_row = []

        # Create a mapping dictionary for this row
        old_features = {
            feature_name: old_row[feature_name] for feature_name in old_feature_list
        }
        label = old_row[label_column]

        # 4. Build the new row using the master template order
        for feature_name in master_feature_list:
            if feature_name in old_features:
                new_row.append(old_features[feature_name])
            else:
                new_row.append(f"{feature_name} disabled")

        # Append the label
        new_row.append(label)
        new_dataset_rows.append(new_row)

    print(f"5. Saving the mapped dataset to {NEW_DATASET_PATH}.")

    # 5. Save the new dataset in the /data directory
    final_dataset = pd.DataFrame(new_dataset_rows)
    final_dataset.to_csv(NEW_DATASET_PATH, index=False, header=False)

    print("\n--- COMPLETE ---")
    print(f"Generated {NEW_DATASET_PATH} with {len(master_feature_list) + 1} columns and {len(new_dataset_rows)} rows.")
    print("This migration resolves feature-matrix dimensional incompatibilities.")
    print("WARNING: A small mapped dataset is insufficient for robust deep-learning training.")

# --- Main Execution Flow ---
if __name__ == "__main__":
    create_configuration_template()

    # Step 2: Create 'data/dataset.csv' by mapping the old data
    create_mapped_dataset()

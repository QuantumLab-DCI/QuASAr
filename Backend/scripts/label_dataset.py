import csv
import random

# --- DEFINE LABELING RULES HERE ---
# This logic should reflect the system's decision-making process.
def assign_adaptation_rule(feature_row):
    """Assign a synthetic complexity label to one feature configuration."""

    # RULE 1: HQC logic (the most important rule)
    # Hybrid quantum configurations represent the highest-complexity workloads.
    if "hybrid_quantum_computing enabled" in feature_row:
        # If HQC is active, this is a HIGH-complexity problem.
        # Assign a random value in the high range.
        return random.randint(300, 350)

    else:
        # --- CLASSICAL CASE (Without HQC) ---
        # This can be as simple or complex as needed.

        # Simple strategy:
        # return random.randint(1, 299)

        # "Smarter" strategy (optional but recommended):
        # Assign complexity based on the number of active classical features.
        score = 0
        if "sports enabled" in feature_row:
            score += 80
        if "entertainment enabled" in feature_row:
            score += 60
        if "tourism enabled" in feature_row:
            score += 40
        if "wood_burning_restriction_viewer enabled" in feature_row:
            score += 50

        # Ensure that the base score is at least 1 and does not exceed the threshold
        if score == 0:
            return random.randint(1, 20) # Very basic configuration
        else:
            # Normalize the score to remain below the threshold of 300
            # For example, if the maximum score is 230 (80+60+40+50), add some noise
            return min(score + random.randint(1, 50), 299)


# --- MAIN FILE-PROCESSING SCRIPT ---
def label_dataset():
    """Label the generated feature configurations and write a training dataset."""
    input_path = "data/configurations.csv"
    output_path = "data/dataset.csv"

    labeled_rows = []

    print(f"Opening {input_path} to generate {output_path}.")

    try:
        with open(input_path, "r", encoding="utf-8") as input_file:
            reader = csv.reader(input_file)

            # Read all rows
            original_rows = list(reader)

            # If configurations.csv has a header, skip or process it
            # Assume for now that it has no header.

            for row in original_rows:
                if not row:
                    continue

                # 1. Assign the adaptation rule
                adaptation_rule = assign_adaptation_rule(row)

                # 2. Create the new row (features + rule)
                labeled_rows.append(row + [adaptation_rule])

        print(f"Processed {len(labeled_rows)} rows.")

        # 3. Write the new dataset.csv file
        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)

            # Optionally write a header
            # num_features = len(labeled_rows[0]) - 1
            # header = [f"feature_{i}" for i in range(num_features)] + ["adaptation_rule"]
            # writer.writerow(header)

            writer.writerows(labeled_rows)

        print(f"Generated {output_path} with synthetic adaptation-rule labels.")

    except FileNotFoundError:
        print(f"ERROR: Input file {input_path} was not found.")
        print("Run create_template.py before labeling the dataset.")
    except Exception as error:
        print(f"Dataset labeling failed: {error}")

# --- Run the Script ---
if __name__ == "__main__":
    label_dataset()

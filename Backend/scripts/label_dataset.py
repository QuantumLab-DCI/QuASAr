"""Generate synthetic adaptation labels for feature configurations."""

import csv
import random

def assign_adaptation_rule(feature_row):
    """Assign a synthetic complexity label to one feature configuration."""

    # Hybrid quantum configurations represent the highest-complexity workloads.
    if "hybrid_quantum_computing enabled" in feature_row:
        return random.randint(300, 350)

    else:
        score = 0
        if "sports enabled" in feature_row:
            score += 80
        if "entertainment enabled" in feature_row:
            score += 60
        if "tourism enabled" in feature_row:
            score += 40
        if "wood_burning_restriction_viewer enabled" in feature_row:
            score += 50

        if score == 0:
            return random.randint(1, 20)
        else:
            # Reserve labels of 300 or greater for hybrid workloads.
            return min(score + random.randint(1, 50), 299)


def label_dataset():
    """Label the generated feature configurations and write a training dataset."""
    input_path = "data/configurations.csv"
    output_path = "data/dataset.csv"

    labeled_rows = []

    print(f"Opening {input_path} to generate {output_path}.")

    try:
        with open(input_path, "r", encoding="utf-8") as input_file:
            reader = csv.reader(input_file)

            original_rows = list(reader)

            # The generated configurations file has no header.

            for row in original_rows:
                if not row:
                    continue

                adaptation_rule = assign_adaptation_rule(row)

                labeled_rows.append(row + [adaptation_rule])

        print(f"Processed {len(labeled_rows)} rows.")

        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerows(labeled_rows)

        print(f"Generated {output_path} with synthetic adaptation-rule labels.")

    except FileNotFoundError:
        print(f"ERROR: Input file {input_path} was not found.")
        print("Run create_template.py before labeling the dataset.")
    except Exception as error:
        print(f"Dataset labeling failed: {error}")

if __name__ == "__main__":
    label_dataset()

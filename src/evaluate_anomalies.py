
import pandas as pd

from .anomaly_detector import detect_anomalies

BASE_DIR = __import__("pathlib").Path(__file__).parent.parent
GROUND_TRUTH_PATH = BASE_DIR / "audit" / "anomaly_ground_truth.csv"


def evaluate_detector():
    ground_truth = pd.read_csv(GROUND_TRUTH_PATH)
    detected = detect_anomalies()

    expected_ids = set(ground_truth["anomaly_id"].dropna())
    detected_ids = set(item["anomaly_id"] for item in detected)

    true_positives = expected_ids & detected_ids
    false_positives = detected_ids - expected_ids
    false_negatives = expected_ids - detected_ids

    precision = (
        len(true_positives) / len(detected_ids)
        if detected_ids else 0
    )

    recall = (
        len(true_positives) / len(expected_ids)
        if expected_ids else 0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    print("\nANOMALY DETECTION EVALUATION")
    print("=" * 55)

    print(f"Expected anomalies: {len(expected_ids)}")
    print(f"Detected anomalies: {len(detected_ids)}")
    print(f"True positives: {len(true_positives)}")
    print(f"False positives: {len(false_positives)}")
    print(f"False negatives: {len(false_negatives)}")

    print("\nMETRICS")
    print("-" * 55)
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1-score:  {f1_score:.2%}")

    print("\nANOMALY-WISE RESULTS")
    print("-" * 55)

    for anomaly_id in sorted(expected_ids):
        if anomaly_id in detected_ids:
            print(f"{anomaly_id}: DETECTED")
        else:
            print(f"{anomaly_id}: MISSED")

    if false_positives:
        print("\nFalse positive IDs:", sorted(false_positives))

    if false_negatives:
        print("\nFalse negative IDs:", sorted(false_negatives))

    print("=" * 55)


if __name__ == "__main__":
    evaluate_detector()

# EVA-STORY: ACA-03-007
import numpy as np

def detect_anomalies(data: list[float], threshold: float = 3.0) -> list[dict]:
    """
    Detect anomalies in the given data based on z-score.

    Args:
        data (list[float]): List of numerical values to analyze.
        threshold (float): Z-score threshold to classify an anomaly. Default is 3.0.

    Returns:
        list[dict]: List of anomalies with their index and value.
    """
    if not data:
        return []

    mean = np.mean(data)
    std_dev = np.std(data)

    if std_dev == 0:
        return []  # No variation in data, no anomalies

    anomalies = []
    for index, value in enumerate(data):
        z_score = (value - mean) / std_dev
        if abs(z_score) > threshold:
            anomalies.append({"index": index, "value": value, "z_score": z_score})

    return anomalies

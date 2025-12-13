# anomaly_detection/anomaly_detector.py

from anomaly_detection.encrypted_threshold import encrypted_threshold_check

def detect_anomaly(enc_hr, enc_spo2, public_key, private_key):
    """
    Detect anomaly using encrypted data
    """

    HR_THRESHOLD = 100
    SPO2_THRESHOLD = 90

    enc_hr_diff = encrypted_threshold_check(
        enc_hr, HR_THRESHOLD, public_key
    )
    enc_spo2_diff = encrypted_threshold_check(
        enc_spo2, SPO2_THRESHOLD, public_key
    )

    # Decrypt ONLY final result (allowed)
    hr_diff = private_key.decrypt(enc_hr_diff)
    spo2_diff = private_key.decrypt(enc_spo2_diff)

    if hr_diff > 0 or spo2_diff < 0:
        return "ANOMALY"
    else:
        return "NORMAL"

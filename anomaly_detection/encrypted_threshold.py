# anomaly_detection/encrypted_threshold.py

def encrypted_threshold_check(enc_value, enc_threshold, public_key):
    """
    Returns encrypted difference: E(value - threshold)
    """
    # E(x - T) = E(x) * E(-T)
    enc_negative_threshold = public_key.encrypt(-enc_threshold)
    enc_diff = enc_value * enc_negative_threshold
    return enc_diff

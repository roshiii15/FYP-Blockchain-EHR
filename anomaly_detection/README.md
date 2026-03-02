## Encrypted Anomaly Detection Module

This module detects abnormal health conditions using homomorphic
operations on encrypted IoT health data.

- Uses Paillier Homomorphic Encryption
- No raw health data is exposed
- Only final anomaly decision is decrypted

Thresholds used:
- Heart Rate > 100 bpm
- SpO₂ < 90%

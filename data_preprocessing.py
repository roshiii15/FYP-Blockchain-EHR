import pandas as pd
import json

# Load dataset exactly with your column names
df = pd.read_csv("Patient_Dataset.csv")

# Rename columns to cleaner internal names
df = df.rename(columns={
    "Patient ID": "patient_id",
    "Timestamp": "timestamp",
    "Heart Rate (bpm)": "heart_rate",
    "Temperature (°C)": "temperature",
    "Blood Pressure (mmHg)": "blood_pressure",
    "Device ID": "device_id",
    "IP Address": "ip_address",
    "Access Type": "access_type",
    "Action": "action",
    "Target": "target"
})

# Split blood pressure "116/84" into two numeric values
df[['systolic', 'diastolic']] = df['blood_pressure'].str.split('/', expand=True).astype(int)

# Convert timestamp to ISO format 
df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True).astype(str)

# Drop original blood_pressure column
df = df.drop(columns=['blood_pressure'])

# Convert to JSON records for blockchain/IPFS storage
records = df.to_dict(orient='records')

# Save JSON
with open("processed_dataset.json", "w") as f:
    json.dump(records, f, indent=4)

print("Preprocessing complete. Output saved to processed_dataset.json")

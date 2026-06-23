import requests
import json
import os

url = "http://localhost:8000/analyze"
payload = {
    "dataset_id": "9f8245ff-58a0-4272-9c9b-7f2145c37f79", # sales_large.csv
    "question": "Why did revenue drop in May?",
    "role": "Executive"
}

print("Triggering multi-agent analysis...")
response = requests.post(url, json=payload)
print("Status Code:", response.status_code)
if response.status_code == 200:
    report = response.json().get("report", "")
    output_path = r"C:\Users\ADMIN\OneDrive\Desktop\capstone\boardroom-ai\scratch\report_output.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Successfully saved report to {output_path}")
else:
    print("Error:", response.text)

import csv

def generate_test_files():
    valid_data = [
        {"id": "101", "channel": "slack", "timestamp": "2023-10-01T10:00", "raw_text": "Please set up a Jira integration with our GitHub repo."},
        {"id": "102", "channel": "email", "timestamp": "2023-10-01T10:05", "raw_text": "I can't log into the corporate VPN, getting error 403."},
        {"id": "103", "channel": "telegram", "timestamp": "2023-10-01T10:10", "raw_text": "Can someone pull the Q3 sales report for the marketing team?"},
        {"id": "104", "channel": "slack", "timestamp": "2023-10-01T10:15", "raw_text": "Need a script to automatically delete inactive users after 90 days."},
        {"id": "105", "channel": "email", "timestamp": "2023-10-01T10:20", "raw_text": "We need to talk about."}
    ]
    with open("test_valid.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "timestamp", "raw_text"])
        writer.writeheader()
        writer.writerows(valid_data)

    invalid_data = [
        {"id": "201", "channel": "slack", "message_content": "This should fail validation because the column name is wrong."}
    ]
    with open("test_invalid_cols.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "message_content"])
        writer.writeheader()
        writer.writerows(invalid_data)

    with open("test_empty.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "timestamp", "raw_text"])
        writer.writeheader()

    print("Test files successfully generated: test_valid.csv, test_invalid_cols.csv, test_empty.csv")

if __name__ == "__main__":
    generate_test_files()
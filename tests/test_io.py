import pytest
import csv
from core.io_handlers import CSVDataReader


@pytest.fixture
def valid_csv(tmp_path):
    """Creates a temporary valid CSV file."""
    filepath = tmp_path / "valid.csv"
    with open(filepath, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "timestamp", "raw_text"])
        writer.writeheader()
        writer.writerow({
            "id": "101",
            "channel": "slack",
            "timestamp": "2023-10-01T10:00",
            "raw_text": "Please set up a Jira integration with our GitHub repo."
        })
    return str(filepath)


@pytest.fixture
def invalid_csv(tmp_path):
    """Creates a temporary CSV file with missing required columns."""
    filepath = tmp_path / "invalid.csv"
    with open(filepath, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "wrong_column"])
        writer.writeheader()
        writer.writerow({
            "id": "201",
            "channel": "slack",
            "wrong_column": "This should fail validation."
        })
    return str(filepath)


@pytest.fixture
def empty_csv(tmp_path):
    """Creates a temporary CSV file with headers but no data."""
    filepath = tmp_path / "empty.csv"
    with open(filepath, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "channel", "timestamp", "raw_text"])
        writer.writeheader()
    return str(filepath)


def test_read_valid_csv(valid_csv):
    reader = CSVDataReader()
    data = reader.read(valid_csv)

    assert len(data) == 1
    assert data[0]["id"] == "101"
    assert data[0]["raw_text"] == "Please set up a Jira integration with our GitHub repo."


def test_read_invalid_csv_raises_error(invalid_csv):
    reader = CSVDataReader()

    with pytest.raises(ValueError, match="Missing required columns in CSV"):
        reader.read(invalid_csv)


def test_read_empty_csv_returns_empty_list(empty_csv):
    reader = CSVDataReader()
    data = reader.read(empty_csv)

    assert isinstance(data, list)
    assert len(data) == 0
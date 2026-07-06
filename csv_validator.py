import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


def read_csv(filepath: str, delimiter: str = ",") -> Tuple[List[str], List[List[str]]]:
    with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, str(email).strip()))


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)\+]", "", str(phone))
    return cleaned.isdigit() and len(cleaned) >= 7


VALIDATORS = {
    "email": validate_email,
    "phone": validate_phone,
    "email_address": validate_email,
    "phone_number": validate_phone,
    "email_addr": validate_email,
}


def detect_column_types(headers: List[str]) -> Dict[str, str]:
    types = {}
    header_lower = [h.lower().strip() for h in headers]
    for i, h in enumerate(header_lower):
        if "email" in h:
            types[headers[i]] = "email"
        elif "phone" in h or "tel" in h or "mobile" in h:
            types[headers[i]] = "phone"
        elif "url" in h or "website" in h:
            types[headers[i]] = "url"
        elif "date" in h:
            types[headers[i]] = "date"
        elif "zip" in h or "postal" in h or "postcode" in h:
            types[headers[i]] = "postal_code"
    return types


def validate_csv(filepath: str, delimiter: str = ",") -> Dict[str, Any]:
    headers, rows = read_csv(filepath, delimiter)
    if not headers:
        return {"valid": False, "error": "Empty file or no headers found", "file": filepath}
    col_count = len(headers)
    column_types = detect_column_types(headers)
    results = {
        "file": filepath,
        "headers": headers,
        "total_rows": len(rows),
        "valid": True,
        "issues": [],
        "row_errors": [],
        "summary": {},
    }
    for i, header in enumerate(headers):
        results["summary"][header] = {"empty_count": 0, "unique_count": 0, "sample_values": set()}
    for row_idx, row in enumerate(rows, start=2):
        if len(row) != col_count:
            results["issues"].append(f"Row {row_idx}: Expected {col_count} columns, got {len(row)}")
            results["valid"] = False
            continue
        for col_idx, (header, value) in enumerate(zip(headers, row)):
            value = value.strip()
            if not value:
                results["summary"][header]["empty_count"] += 1
                continue
            results["summary"][header]["sample_values"].add(value[:50])
            col_type = column_types.get(header)
            if col_type and col_type in VALIDATORS:
                validator = VALIDATORS[col_type]
                if not validator(value):
                    results["row_errors"].append(f"Row {row_idx}, '{header}': Invalid {col_type} ('{value}')")
                    results["valid"] = False
    for header in headers:
        s = results["summary"][header]
        s["unique_count"] = len(s["sample_values"])
        s["sample_values"] = list(s["sample_values"])[:5]
    if not results["row_errors"]:
        results["row_errors"].append("All field validations passed.")
    return results


def display_results(results: Dict[str, Any]):
    print(f"\nFile: {results['file']}")
    print(f"Headers: {', '.join(results['headers'])}")
    print(f"Total rows: {results['total_rows']}")
    status = "VALID" if results["valid"] else "ISSUES FOUND"
    color = "✓" if results["valid"] else "✗"
    print(f"Status: {color} {status}")
    if results["issues"]:
        print(f"\nStructural issues ({len(results['issues'])}):")
        for issue in results["issues"]:
            print(f"  - {issue}")
    if results.get("row_errors"):
        validation_errors = [e for e in results["row_errors"] if e != "All field validations passed."]
        if validation_errors:
            print(f"\nValidation errors ({len(validation_errors)}):")
            for err in validation_errors[:10]:
                print(f"  - {err}")
            if len(validation_errors) > 10:
                print(f"  ... and {len(validation_errors) - 10} more")
    print(f"\nColumn summary:")
    for header, info in results["summary"].items():
        print(f"  {header}: {info['empty_count']} empty, {info['unique_count']} unique values")


def main():
    print("=" * 50)
    print("  CSV VALIDATOR")
    print("=" * 50)
    filepath = input("CSV file path: ").strip()
    if not filepath:
        print("No file specified.")
        return
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        return
    delim = input("Delimiter (default: comma): ").strip()
    if not delim:
        delim = ","
    results = validate_csv(filepath, delim)
    display_results(results)


if __name__ == "__main__":
    main()

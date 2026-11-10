"""Summarize synthetic structured security logs."""
import argparse
import ipaddress
import json
import re
from collections import Counter
from datetime import datetime

LOG_LINE = re.compile(r"^(\S+) (INFO|WARN|ERROR|CRITICAL) src=(\S+) msg=(.+)$")

def parse_line(line):
    match = LOG_LINE.fullmatch(line.strip())
    if not match:
        return None
    timestamp, level, source_ip, message = match.groups()
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        ipaddress.ip_address(source_ip)
    except ValueError:
        return None
    return {"timestamp": timestamp, "level": level, "source_ip": source_ip, "message": message}

def analyze_lines(lines):
    severities = Counter()
    sources = Counter()
    processed = 0
    malformed = 0
    for line in lines:
        if not line.strip():
            continue
        processed += 1
        event = parse_line(line)
        if event is None:
            malformed += 1
            continue
        severities[event["level"]] += 1
        sources[event["source_ip"]] += 1
    return {"lines_processed": processed, "valid_events": processed - malformed,
            "malformed_lines": malformed,
            "severities": dict(sorted(severities.items())),
            "top_sources": [{"ip": ip, "events": count} for ip, count in sources.most_common(5)]}

def main():
    parser = argparse.ArgumentParser(description="Structured security log analysis")
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()
    try:
        with open(args.file, encoding="utf-8") as handle:
            report = analyze_lines(handle)
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Valid events: {} / {}".format(report["valid_events"], report["lines_processed"]))
        print("Malformed lines:", report["malformed_lines"])
        print("Severities:", report["severities"])
        print("Top sources:", report["top_sources"])

if __name__ == "__main__":
    main()

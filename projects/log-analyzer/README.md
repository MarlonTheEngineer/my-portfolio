# Security Log Analyzer

A standard-library Python project that validates and summarizes a small **structured example log format**, counts events by severity, and identifies top source IP addresses.

This is a learning exercise and **not** a production SIEM or a generic Windows Event Log parser.

## Expected format
`2026-11-10T08:21:00Z ERROR src=192.168.1.22 msg=Authentication failed`

## Run
```powershell
python analyzer.py sample.log
python analyzer.py sample.log --json
```

## Tests
```powershell
python -m unittest discover -s tests -v
```

## Future improvements
- Handle Windows Event Log CSV exports
- Add login-failure threshold alerts
- Date filtering and CSV reports
- Graphical dashboard

The included log is synthetic. Do not upload real security logs or confidential data.

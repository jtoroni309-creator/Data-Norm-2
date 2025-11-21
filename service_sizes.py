#!/usr/bin/env python3
import os
from pathlib import Path

services_dir = Path('services')
service_sizes = []

for service_path in sorted(services_dir.iterdir()):
    if service_path.is_dir():
        total_lines = 0
        py_files = 0

        for py_file in service_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    py_files += 1
            except:
                pass

        if py_files > 0:
            service_sizes.append((total_lines, py_files, service_path.name))

# Sort by lines descending
service_sizes.sort(reverse=True)

print("=== SERVICE SIZE BREAKDOWN (Top 15 by Python lines) ===")
print(f"{'Rank':<6} {'Service':<40} {'Lines':>10} {'Files':>8}")
print("-" * 70)

for i, (lines, files, name) in enumerate(service_sizes[:15], 1):
    print(f"{i:<6} {name:<40} {lines:>10,} {files:>8}")

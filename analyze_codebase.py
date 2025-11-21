#!/usr/bin/env python3
"""
Comprehensive codebase analyzer for SLOC and statistics
"""
import os
import json
from pathlib import Path
from collections import defaultdict
import re

# Extensions to analyze
CODE_EXTENSIONS = {
    # Backend
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript JSX',
    '.jsx': 'JavaScript JSX',
    '.go': 'Go',
    '.java': 'Java',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.cs': 'C#',

    # Frontend/Markup
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SASS',
    '.less': 'LESS',
    '.vue': 'Vue',
    '.svelte': 'Svelte',

    # Config/Data
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.sql': 'SQL',

    # Scripts
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Zsh',
    '.fish': 'Fish',
    '.ps1': 'PowerShell',

    # Docs
    '.md': 'Markdown',
    '.rst': 'reStructuredText',
    '.txt': 'Text',

    # Docker/K8s
    'Dockerfile': 'Dockerfile',
    '.dockerignore': 'Docker',

    # Other
    '.proto': 'Protocol Buffer',
    '.graphql': 'GraphQL',
    '.prisma': 'Prisma',
}

# Directories to exclude
EXCLUDE_DIRS = {
    'node_modules', '.git', '.venv', 'venv', '__pycache__',
    'dist', 'build', '.next', '.cache', 'coverage', '.pytest_cache',
    'vendor', 'target', 'bin', 'obj', '.terraform', 'public',
    '.nuxt', '.output', '.vercel', '.netlify'
}

# Files to exclude
EXCLUDE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'poetry.lock', 'Pipfile.lock', 'go.sum', 'Cargo.lock'
}

def is_binary(file_path):
    """Check if file is binary"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
        return False
    except:
        return True

def count_lines(file_path):
    """Count total, code, comment, and blank lines"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())

        # Simple comment detection (not perfect but reasonable)
        comments = 0
        in_multiline = False
        ext = Path(file_path).suffix.lower()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Python style
            if ext == '.py':
                if stripped.startswith('#'):
                    comments += 1
                elif '"""' in stripped or "'''" in stripped:
                    if in_multiline:
                        comments += 1
                        if stripped.count('"""') % 2 == 1 or stripped.count("'''") % 2 == 1:
                            in_multiline = False
                    else:
                        comments += 1
                        if stripped.count('"""') % 2 == 1 or stripped.count("'''") % 2 == 1:
                            in_multiline = True
                elif in_multiline:
                    comments += 1

            # JS/TS/Java/C style
            elif ext in ['.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', '.cs', '.go', '.rs']:
                if stripped.startswith('//'):
                    comments += 1
                elif stripped.startswith('/*'):
                    comments += 1
                    if '*/' not in stripped:
                        in_multiline = True
                elif in_multiline:
                    comments += 1
                    if '*/' in stripped:
                        in_multiline = False

            # HTML/XML style
            elif ext in ['.html', '.xml', '.vue', '.svelte']:
                if '<!--' in stripped:
                    comments += 1
                    if '-->' not in stripped:
                        in_multiline = True
                elif in_multiline:
                    comments += 1
                    if '-->' in stripped:
                        in_multiline = False

            # Shell/Python style
            elif ext in ['.sh', '.bash', '.zsh', '.yaml', '.yml']:
                if stripped.startswith('#'):
                    comments += 1

        code = total - blank - comments
        return total, code, comments, blank

    except Exception as e:
        return 0, 0, 0, 0

def get_language(file_path):
    """Determine language from file extension or name"""
    file_name = os.path.basename(file_path)

    # Check full filename first
    if file_name in CODE_EXTENSIONS:
        return CODE_EXTENSIONS[file_name]

    # Check extension
    ext = Path(file_path).suffix.lower()
    if ext in CODE_EXTENSIONS:
        return CODE_EXTENSIONS[ext]

    # Special cases
    if file_name.startswith('Dockerfile'):
        return 'Dockerfile'
    if file_name == 'Makefile':
        return 'Makefile'

    return None

def analyze_directory(root_dir):
    """Analyze entire directory structure"""
    stats = {
        'by_language': defaultdict(lambda: {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0
        }),
        'by_directory': defaultdict(lambda: {
            'files': 0,
            'total_lines': 0,
            'code_lines': 0
        }),
        'total_files': 0,
        'total_dirs': 0,
        'total_lines': 0,
        'total_code_lines': 0,
        'total_comment_lines': 0,
        'total_blank_lines': 0
    }

    root_path = Path(root_dir)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        rel_path = os.path.relpath(dirpath, root_dir)
        if rel_path != '.':
            stats['total_dirs'] += 1

        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue

            file_path = os.path.join(dirpath, filename)

            # Skip binary files
            if is_binary(file_path):
                continue

            language = get_language(file_path)
            if not language:
                continue

            total, code, comments, blank = count_lines(file_path)

            if total == 0:
                continue

            # Update language stats
            stats['by_language'][language]['files'] += 1
            stats['by_language'][language]['total_lines'] += total
            stats['by_language'][language]['code_lines'] += code
            stats['by_language'][language]['comment_lines'] += comments
            stats['by_language'][language]['blank_lines'] += blank

            # Update directory stats
            top_dir = rel_path.split(os.sep)[0] if rel_path != '.' else 'root'
            stats['by_directory'][top_dir]['files'] += 1
            stats['by_directory'][top_dir]['total_lines'] += total
            stats['by_directory'][top_dir]['code_lines'] += code

            # Update totals
            stats['total_files'] += 1
            stats['total_lines'] += total
            stats['total_code_lines'] += code
            stats['total_comment_lines'] += comments
            stats['total_blank_lines'] += blank

    return stats

def format_number(num):
    """Format number with thousand separators"""
    return f"{num:,}"

def print_report(stats):
    """Print formatted report"""
    print("=" * 80)
    print("CODEBASE STATISTICS REPORT")
    print("=" * 80)
    print()

    print("OVERALL SUMMARY")
    print("-" * 80)
    print(f"Total Files:           {format_number(stats['total_files'])}")
    print(f"Total Directories:     {format_number(stats['total_dirs'])}")
    print(f"Total Lines:           {format_number(stats['total_lines'])}")
    print(f"Source Lines of Code:  {format_number(stats['total_code_lines'])}")
    print(f"Comment Lines:         {format_number(stats['total_comment_lines'])}")
    print(f"Blank Lines:           {format_number(stats['total_blank_lines'])}")
    print()

    print("BREAKDOWN BY LANGUAGE")
    print("-" * 80)
    print(f"{'Language':<25} {'Files':>8} {'Total':>12} {'Code':>12} {'Comments':>12} {'Blank':>12}")
    print("-" * 80)

    # Sort by code lines descending
    sorted_langs = sorted(
        stats['by_language'].items(),
        key=lambda x: x[1]['code_lines'],
        reverse=True
    )

    for lang, data in sorted_langs:
        print(f"{lang:<25} {data['files']:>8,} {data['total_lines']:>12,} "
              f"{data['code_lines']:>12,} {data['comment_lines']:>12,} {data['blank_lines']:>12,}")

    print()
    print("BREAKDOWN BY TOP-LEVEL DIRECTORY")
    print("-" * 80)
    print(f"{'Directory':<30} {'Files':>8} {'Total':>12} {'Code':>12}")
    print("-" * 80)

    # Sort by code lines descending
    sorted_dirs = sorted(
        stats['by_directory'].items(),
        key=lambda x: x[1]['code_lines'],
        reverse=True
    )

    for dir_name, data in sorted_dirs:
        print(f"{dir_name:<30} {data['files']:>8,} {data['total_lines']:>12,} {data['code_lines']:>12,}")

    print()
    print("=" * 80)

if __name__ == '__main__':
    root_dir = '/home/user/Data-Norm-2'
    print(f"Analyzing codebase at: {root_dir}")
    print("This may take a minute...")
    print()

    stats = analyze_directory(root_dir)
    print_report(stats)

    # Save to JSON
    output_file = '/home/user/Data-Norm-2/codebase_stats.json'
    # Convert defaultdicts to regular dicts for JSON serialization
    json_stats = {
        'by_language': dict(stats['by_language']),
        'by_directory': dict(stats['by_directory']),
        'total_files': stats['total_files'],
        'total_dirs': stats['total_dirs'],
        'total_lines': stats['total_lines'],
        'total_code_lines': stats['total_code_lines'],
        'total_comment_lines': stats['total_comment_lines'],
        'total_blank_lines': stats['total_blank_lines']
    }

    with open(output_file, 'w') as f:
        json.dump(json_stats, f, indent=2)

    print(f"\nDetailed statistics saved to: {output_file}")

#!/usr/bin/env python3
"""
Validate OpenAPI specifications.

This script validates OpenAPI specs against the OpenAPI 3.1.0 specification
and checks for common issues.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


def load_spec(filepath: Path) -> Dict:
    """Load OpenAPI spec from file."""
    with open(filepath) as f:
        if filepath.suffix == ".json":
            return json.load(f)
        else:
            return yaml.safe_load(f)


def validate_required_fields(spec: Dict) -> List[str]:
    """Validate that required top-level fields are present."""
    errors = []
    required = ["openapi", "info", "paths"]

    for field in required:
        if field not in spec:
            errors.append(f"Missing required field: {field}")

    # Validate info object
    if "info" in spec:
        info_required = ["title", "version"]
        for field in info_required:
            if field not in spec["info"]:
                errors.append(f"Missing required info field: {field}")

    return errors


def validate_paths(spec: Dict) -> List[str]:
    """Validate paths object."""
    errors = []

    if "paths" not in spec:
        return errors

    paths = spec["paths"]

    if not isinstance(paths, dict):
        errors.append("Paths must be an object")
        return errors

    if not paths:
        errors.append("Paths object is empty")

    # Validate each path
    for path, path_item in paths.items():
        if not path.startswith("/"):
            errors.append(f"Path must start with /: {path}")

        if not isinstance(path_item, dict):
            errors.append(f"Path item must be an object: {path}")
            continue

        # Check for valid HTTP methods
        valid_methods = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]
        for method in path_item.keys():
            if method.lower() not in valid_methods and method not in ["$ref", "summary", "description", "servers", "parameters"]:
                errors.append(f"Invalid HTTP method in path {path}: {method}")

    return errors


def validate_components(spec: Dict) -> List[str]:
    """Validate components object."""
    errors = []

    if "components" not in spec:
        return errors

    components = spec["components"]

    if not isinstance(components, dict):
        errors.append("Components must be an object")
        return errors

    # Validate schemas
    if "schemas" in components:
        schemas = components["schemas"]
        if not isinstance(schemas, dict):
            errors.append("Components.schemas must be an object")
        else:
            for schema_name, schema in schemas.items():
                if not isinstance(schema, dict):
                    errors.append(f"Schema must be an object: {schema_name}")

    return errors


def validate_security(spec: Dict) -> List[str]:
    """Validate security configuration."""
    errors = []

    # Check if security is defined
    if "security" in spec:
        security = spec["security"]
        if not isinstance(security, list):
            errors.append("Security must be an array")

    # Check if security schemes are defined
    if "components" in spec and "securitySchemes" in spec["components"]:
        schemes = spec["components"]["securitySchemes"]

        # Validate each scheme
        for scheme_name, scheme in schemes.items():
            if "type" not in scheme:
                errors.append(f"Security scheme missing type: {scheme_name}")
            else:
                scheme_type = scheme["type"]
                if scheme_type not in ["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"]:
                    errors.append(f"Invalid security scheme type: {scheme_type} in {scheme_name}")

    return errors


def check_deprecations(spec: Dict) -> List[str]:
    """Check for deprecated fields or patterns."""
    warnings = []

    # Check OpenAPI version
    if "openapi" in spec:
        version = spec["openapi"]
        if version.startswith("2."):
            warnings.append("Using OpenAPI 2.x (Swagger). Consider upgrading to 3.x")
        elif version.startswith("3.0"):
            warnings.append("Using OpenAPI 3.0.x. Consider upgrading to 3.1.x for JSON Schema support")

    return warnings


def analyze_spec_stats(spec: Dict) -> Dict:
    """Generate statistics about the OpenAPI spec."""
    stats = {
        "version": spec.get("openapi", "unknown"),
        "title": spec.get("info", {}).get("title", "unknown"),
        "paths_count": len(spec.get("paths", {})),
        "schemas_count": len(spec.get("components", {}).get("schemas", {})),
        "security_schemes_count": len(spec.get("components", {}).get("securitySchemes", {})),
        "tags_count": len(spec.get("tags", [])),
        "servers_count": len(spec.get("servers", [])),
    }

    # Count operations
    operations_count = 0
    for path_item in spec.get("paths", {}).values():
        operations_count += sum(1 for k in path_item.keys() if k in ["get", "put", "post", "delete", "options", "head", "patch"])

    stats["operations_count"] = operations_count

    return stats


def validate_spec(filepath: Path, verbose: bool = False) -> Tuple[bool, List[str], List[str], Dict]:
    """
    Validate an OpenAPI specification.

    Args:
        filepath: Path to OpenAPI spec file
        verbose: Print detailed validation info

    Returns:
        Tuple of (is_valid, errors, warnings, stats)
    """
    print(f"Validating {filepath}...")
    print()

    try:
        spec = load_spec(filepath)
    except Exception as e:
        return False, [f"Failed to load spec: {e}"], [], {}

    errors = []
    warnings = []

    # Run validation checks
    errors.extend(validate_required_fields(spec))
    errors.extend(validate_paths(spec))
    errors.extend(validate_components(spec))
    errors.extend(validate_security(spec))

    # Run deprecation checks
    warnings.extend(check_deprecations(spec))

    # Generate stats
    stats = analyze_spec_stats(spec)

    # Print results
    if verbose or errors or warnings:
        print("Specification Statistics:")
        print(f"  Version: {stats['version']}")
        print(f"  Title: {stats['title']}")
        print(f"  Paths: {stats['paths_count']}")
        print(f"  Operations: {stats['operations_count']}")
        print(f"  Schemas: {stats['schemas_count']}")
        print(f"  Security Schemes: {stats['security_schemes_count']}")
        print(f"  Tags: {stats['tags_count']}")
        print(f"  Servers: {stats['servers_count']}")
        print()

    if errors:
        print(f"❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        print()

    if warnings:
        print(f"⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    is_valid = len(errors) == 0

    if is_valid:
        print("✓ OpenAPI specification is valid")
    else:
        print("✗ OpenAPI specification has errors")

    return is_valid, errors, warnings, stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate OpenAPI specifications"
    )
    parser.add_argument(
        "spec_file",
        type=Path,
        help="Path to OpenAPI specification file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if not args.spec_file.exists():
        print(f"❌ File not found: {args.spec_file}")
        sys.exit(1)

    is_valid, errors, warnings, stats = validate_spec(args.spec_file, args.verbose)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

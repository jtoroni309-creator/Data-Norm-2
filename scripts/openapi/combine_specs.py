#!/usr/bin/env python3
"""
Combine multiple OpenAPI specifications into a unified spec.

This script merges individual service OpenAPI specs into a single
comprehensive API specification with proper path prefixing.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

import yaml


def load_spec(filepath: Path) -> Dict:
    """Load OpenAPI spec from JSON or YAML file."""
    with open(filepath) as f:
        if filepath.suffix == ".json":
            return json.load(f)
        else:
            return yaml.safe_load(f)


def prefix_paths(paths: Dict, prefix: str) -> Dict:
    """
    Add prefix to all paths in OpenAPI spec.

    Args:
        paths: Paths dictionary from OpenAPI spec
        prefix: Path prefix (e.g., "/identity")

    Returns:
        Prefixed paths dictionary
    """
    return {f"{prefix}{path}": content for path, content in paths.items()}


def merge_tags(tags_list: List[List[Dict]]) -> List[Dict]:
    """
    Merge tags from multiple specs, removing duplicates.

    Args:
        tags_list: List of tags arrays from different specs

    Returns:
        Merged unique tags
    """
    tags_dict = {}

    for tags in tags_list:
        if tags:
            for tag in tags:
                name = tag.get("name")
                if name and name not in tags_dict:
                    tags_dict[name] = tag

    return list(tags_dict.values())


def merge_components(components_list: List[Dict]) -> Dict:
    """
    Merge components (schemas, securitySchemes, etc.) from multiple specs.

    Args:
        components_list: List of components from different specs

    Returns:
        Merged components
    """
    merged = {
        "schemas": {},
        "securitySchemes": {},
        "responses": {},
        "parameters": {},
        "examples": {},
        "requestBodies": {},
        "headers": {},
        "links": {},
        "callbacks": {},
    }

    for components in components_list:
        if not components:
            continue

        for comp_type, comp_dict in components.items():
            if comp_type not in merged:
                merged[comp_type] = {}

            if isinstance(comp_dict, dict):
                # Handle potential naming conflicts
                for name, definition in comp_dict.items():
                    if name in merged[comp_type]:
                        # Add service prefix if conflict
                        unique_name = f"{name}_dup{len([k for k in merged[comp_type] if k.startswith(name)])}"
                        merged[comp_type][unique_name] = definition
                    else:
                        merged[comp_type][name] = definition

    # Remove empty sections
    return {k: v for k, v in merged.items() if v}


def combine_specs(specs_dir: Path, output_file: Path, metadata: Dict = None) -> Dict:
    """
    Combine all OpenAPI specs in directory into unified spec.

    Args:
        specs_dir: Directory containing individual service specs
        output_file: Path to save combined spec
        metadata: Optional metadata to override (title, description, version, etc.)

    Returns:
        Combined OpenAPI specification
    """
    print("=" * 60)
    print("Combining OpenAPI Specifications")
    print("=" * 60)
    print()

    # Find all spec files
    spec_files = list(specs_dir.glob("*.json")) + list(specs_dir.glob("*.yaml"))

    if not spec_files:
        print(f"❌ No spec files found in {specs_dir}")
        sys.exit(1)

    print(f"Found {len(spec_files)} specification files")
    print()

    # Initialize combined spec
    combined = {
        "openapi": "3.1.0",
        "info": metadata.get("info") if metadata else {
            "title": "Aura Audit AI - Unified API",
            "description": "Combined API specification for all microservices",
            "version": "1.0.0",
            "contact": {
                "name": "Aura Audit AI Support",
                "email": "support@aura-audit.ai",
            },
            "license": {"name": "Proprietary"},
        },
        "servers": metadata.get("servers") if metadata else [
            {"url": "http://localhost:8000", "description": "Local development"},
            {"url": "https://api-dev.aura-audit.ai", "description": "Development"},
            {"url": "https://api.aura-audit.ai", "description": "Production"},
        ],
        "security": metadata.get("security") if metadata else [
            {"bearerAuth": []},
            {"oauth2": ["read", "write"]},
        ],
        "paths": {},
        "components": {},
        "tags": [],
    }

    # Collect all specs
    all_tags = []
    all_components = []

    # Process each service spec
    for spec_file in sorted(spec_files):
        service_name = spec_file.stem
        print(f"Processing {service_name}...")

        try:
            spec = load_spec(spec_file)

            # Add paths with service prefix
            if "paths" in spec:
                prefix = f"/{service_name}"
                prefixed_paths = prefix_paths(spec["paths"], prefix)
                combined["paths"].update(prefixed_paths)
                print(f"  ✓ Added {len(prefixed_paths)} paths")

            # Collect tags
            if "tags" in spec:
                all_tags.append(spec["tags"])
                print(f"  ✓ Added {len(spec['tags'])} tags")

            # Collect components
            if "components" in spec:
                all_components.append(spec["components"])
                schemas_count = len(spec["components"].get("schemas", {}))
                print(f"  ✓ Added {schemas_count} schemas")

        except Exception as e:
            print(f"  ❌ Error processing {service_name}: {e}")
            continue

    # Merge collected items
    print()
    print("Merging components...")
    combined["tags"] = merge_tags(all_tags)
    combined["components"] = merge_components(all_components)

    print(f"  ✓ Total tags: {len(combined['tags'])}")
    print(f"  ✓ Total schemas: {len(combined['components'].get('schemas', {}))}")
    print(f"  ✓ Total paths: {len(combined['paths'])}")

    # Add security schemes if not in metadata
    if "securitySchemes" not in combined["components"]:
        combined["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "oauth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://auth.aura-audit.ai/oauth2/authorize",
                        "tokenUrl": "https://auth.aura-audit.ai/oauth2/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access",
                            "admin": "Administrative access",
                        },
                    }
                },
            },
        }

    # Save combined spec
    print()
    print(f"Saving combined specification to {output_file}...")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.suffix == ".json":
        with open(output_file, "w") as f:
            json.dump(combined, f, indent=2)
    else:
        with open(output_file, "w") as f:
            yaml.dump(combined, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Saved {output_file}")
    print()
    print("=" * 60)
    print("✓ OpenAPI Specification Combined Successfully")
    print("=" * 60)

    return combined


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Combine multiple OpenAPI specifications"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "openapi" / "generated",
        help="Directory containing individual service specs",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent.parent / "openapi" / "atlas-combined.yaml",
        help="Output file path",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        help="Optional metadata YAML file to override defaults",
    )

    args = parser.parse_args()

    # Load metadata if provided
    metadata = None
    if args.metadata and args.metadata.exists():
        with open(args.metadata) as f:
            metadata = yaml.safe_load(f)

    # Combine specs
    combine_specs(args.input_dir, args.output, metadata)


if __name__ == "__main__":
    main()

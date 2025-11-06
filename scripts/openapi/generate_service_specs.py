#!/usr/bin/env python3
"""
Generate OpenAPI specifications from FastAPI services.

This script extracts OpenAPI specs from running FastAPI applications
and saves them to individual JSON/YAML files.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import yaml

# Service configuration
SERVICES = [
    {"name": "identity", "port": 8009, "path": "/"},
    {"name": "ingestion", "port": 8001, "path": "/"},
    {"name": "normalize", "port": 8002, "path": "/"},
    {"name": "analytics", "port": 8003, "path": "/"},
    {"name": "llm", "port": 8004, "path": "/"},
    {"name": "engagement", "port": 8005, "path": "/"},
    {"name": "disclosures", "port": 8006, "path": "/"},
    {"name": "reporting", "port": 8007, "path": "/"},
    {"name": "qc", "port": 8008, "path": "/"},
    {"name": "connectors", "port": 8010, "path": "/"},
    {"name": "security", "port": 8011, "path": "/"},
    {"name": "reg-ab-audit", "port": 8012, "path": "/"},
]

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "openapi" / "generated"


async def fetch_openapi_spec(service: Dict, base_url: str = "http://localhost") -> Optional[Dict]:
    """
    Fetch OpenAPI specification from a running FastAPI service.

    Args:
        service: Service configuration
        base_url: Base URL for the service

    Returns:
        OpenAPI specification as dictionary, or None if failed
    """
    url = f"{base_url}:{service['port']}{service['path']}openapi.json"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Failed to fetch {service['name']}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error fetching {service['name']}: {e}", file=sys.stderr)
        return None


def save_spec(service_name: str, spec: Dict, format: str = "both") -> None:
    """
    Save OpenAPI specification to file.

    Args:
        service_name: Name of the service
        spec: OpenAPI specification
        format: Output format ('json', 'yaml', or 'both')
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if format in ["json", "both"]:
        json_path = OUTPUT_DIR / f"{service_name}.json"
        with open(json_path, "w") as f:
            json.dump(spec, f, indent=2)
        print(f"✓ Saved {json_path}")

    if format in ["yaml", "both"]:
        yaml_path = OUTPUT_DIR / f"{service_name}.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Saved {yaml_path}")


async def generate_all_specs(
    base_url: str = "http://localhost", format: str = "both"
) -> Dict[str, Dict]:
    """
    Generate OpenAPI specs for all services.

    Args:
        base_url: Base URL for services
        format: Output format

    Returns:
        Dictionary mapping service names to their OpenAPI specs
    """
    specs = {}

    print("=" * 60)
    print("Generating OpenAPI Specifications from FastAPI Services")
    print("=" * 60)
    print()

    # Fetch all specs concurrently
    tasks = [fetch_openapi_spec(service, base_url) for service in SERVICES]
    results = await asyncio.gather(*tasks)

    # Save specs
    for service, spec in zip(SERVICES, results):
        if spec:
            specs[service["name"]] = spec
            save_spec(service["name"], spec, format)
        else:
            print(f"⚠️  Skipping {service['name']} (not available)")

    print()
    print(f"✓ Generated {len(specs)}/{len(SERVICES)} specifications")
    print(f"✓ Output directory: {OUTPUT_DIR}")
    print()

    return specs


async def generate_from_code(service_path: Path) -> Optional[Dict]:
    """
    Generate OpenAPI spec directly from FastAPI code (without running service).

    Args:
        service_path: Path to service directory

    Returns:
        OpenAPI specification
    """
    # Add service to Python path
    sys.path.insert(0, str(service_path / "app"))

    try:
        # Import main module
        from main import app

        # Get OpenAPI spec
        spec = app.openapi()
        return spec
    except Exception as e:
        print(f"❌ Error generating from code: {e}", file=sys.stderr)
        return None
    finally:
        # Clean up sys.path
        sys.path.pop(0)


async def generate_from_code_all(services_dir: Path, format: str = "both") -> Dict[str, Dict]:
    """
    Generate specs from code for all services.

    Args:
        services_dir: Path to services directory
        format: Output format

    Returns:
        Dictionary of generated specs
    """
    specs = {}

    print("=" * 60)
    print("Generating OpenAPI Specifications from Code")
    print("=" * 60)
    print()

    for service in SERVICES:
        service_path = services_dir / service["name"]

        if not service_path.exists():
            print(f"⚠️  Service not found: {service_path}")
            continue

        print(f"Processing {service['name']}...")

        spec = await generate_from_code(service_path)

        if spec:
            specs[service["name"]] = spec
            save_spec(service["name"], spec, format)
            print(f"✓ Generated {service['name']}")
        else:
            print(f"❌ Failed to generate {service['name']}")

    print()
    print(f"✓ Generated {len(specs)}/{len(SERVICES)} specifications")
    print()

    return specs


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate OpenAPI specifications from FastAPI services"
    )
    parser.add_argument(
        "--mode",
        choices=["running", "code"],
        default="running",
        help="Generation mode: from running services or from code",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost",
        help="Base URL for running services",
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "both"],
        default="both",
        help="Output format",
    )
    parser.add_argument(
        "--services-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "services",
        help="Path to services directory (for code mode)",
    )

    args = parser.parse_args()

    # Run generation
    if args.mode == "running":
        asyncio.run(generate_all_specs(args.base_url, args.format))
    else:
        asyncio.run(generate_from_code_all(args.services_dir, args.format))


if __name__ == "__main__":
    main()

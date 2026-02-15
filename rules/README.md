# Rules Engine
This directory contains the deterministic logic that bridges failure patterns to concrete AWS services.
- **service_catalog.py**: The source of truth for available services.
- **failure_to_pattern.py**: Logic to identify which pattern applies to a situation.
- **pattern_to_service.py**: Logic to recommend services based on the identified pattern.

# Data Directory
This directory contains the raw knowledge base for the system.
- **incidents/**: JSON files describing historical AWS incidents (e.g., "aws_us_east_2017.json").
- **lessons/**: JSON files containing lessons learned from failures (e.g., "retry_storms.json").
- **adr/**: Architectural Decision Records in JSON format (e.g., "async_vs_sync_processing.json").

All data here is human-curated and serves as the ground truth before embedding.

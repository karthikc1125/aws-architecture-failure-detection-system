#!/usr/bin/env python3
"""
Simple app launcher wrapper for the Failure-Driven AWS Architect
Run with: python app.py
"""
import subprocess
import sys

if __name__ == "__main__":
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    subprocess.run(cmd)

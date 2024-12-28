#!/bin/bash
# Run FastAPI with the specified port
conda activate api
fastapi dev main.py --port 8001
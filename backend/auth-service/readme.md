# Auth Service

This is the authentication service for Summiva.

## Running Locally

### Python virtual env
```bash
python3 -m venv venv
source venv/bin/activate

```

### Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run the service
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8004
```
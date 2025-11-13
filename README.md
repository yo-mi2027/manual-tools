cd manual-tools
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt

uvicorn app.main:app --host 127.0.0.1 --port 5173 --reload

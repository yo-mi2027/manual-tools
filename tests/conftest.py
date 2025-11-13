# tests/conftest.py

import sys
from pathlib import Path

# このファイル（tests/conftest.py）から見たプロジェクトルート
ROOT = Path(__file__).resolve().parents[1]

# 先頭に差し込んで app パッケージを import 可能にする
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

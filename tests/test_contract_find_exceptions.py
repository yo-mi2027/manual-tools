from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_find_exceptions_has_result():
    """
    find_exceptions が少なくとも1件は例外系文脈を返すことを確認。
    （辞書に依存するので、将来語彙を変えたら期待件数を調整する）
    """
    resp = client.post(
        "/find_exceptions",
        json={
            "manual_name": "給付金編",
            "limit": 20,
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    # 例外に相当するものが1件は拾えていること
    assert len(data["results"]) > 0

    first = data["results"][0]
    assert "section_id" in first
    assert "text" in first
    assert isinstance(first["text"], str)
    assert len(first["text"]) > 0

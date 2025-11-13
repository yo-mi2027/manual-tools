from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_section_ok():
    """存在する章IDで本文が取得できることを確認"""
    resp = client.get(
        "/get_section",
        params={"manual_name": "給付金編", "section_id": "03-1"},
    )
    assert resp.status_code == 200

    data = resp.json()
    # 念のため manual / section_id が返っていればチェック
    if "manual" in data:
        assert data["manual"] == "給付金編"
    if "section_id" in data:
        assert data["section_id"] == "03-1"

    # 本文テキストがあること
    assert "text" in data
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0


def test_get_section_not_found():
    """存在しない章IDで 404 が返ることを確認"""
    resp = client.get(
        "/get_section",
        params={"manual_name": "給付金編", "section_id": "99-9"},
    )
    assert resp.status_code == 404
    data = resp.json()
    # エラーメッセージの形だけ軽く見る
    assert "detail" in data

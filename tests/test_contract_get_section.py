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

    # 契約どおり manual / section_id / title / text が必須であること
    assert "manual" in data
    assert "section_id" in data
    assert "title" in data
    assert "text" in data

    assert data["manual"] == "給付金編"
    assert data["section_id"] == "03-1"

    assert isinstance(data["title"], str)
    assert len(data["title"]) > 0

    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0

    # 任意フィールドの形だけ軽く確認（存在する場合）
    if "file" in data:
        assert isinstance(data["file"], str)
        assert len(data["file"]) > 0

    if "encoding" in data:
        assert isinstance(data["encoding"], str)
        assert len(data["encoding"]) > 0

    if "id" in data:
        # id は section_id と同値であることを期待
        assert data["id"] == data["section_id"]


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
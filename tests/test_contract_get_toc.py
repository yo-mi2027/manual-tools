from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_toc_flat():
    """階層なし（hierarchical=false）の ToC が取れることを確認"""
    resp = client.get("/get_toc", params={"manual_name": "給付金編"})
    assert resp.status_code == 200

    data = resp.json()
    assert data["manual"] == "給付金編"
    assert isinstance(data["toc"], list)
    assert len(data["toc"]) > 0

    first = data["toc"][0]
    # 章IDとタイトルが最低限あること
    assert "id" in first
    assert "title" in first
    # 階層なしモードでは children が返ってこない（返ってきても害はないが期待としては無し）
    assert "children" not in first


def test_get_toc_hierarchical():
    """階層あり（hierarchical=true）の ToC が取れることを確認"""
    resp = client.get(
        "/get_toc",
        params={"manual_name": "給付金編", "hierarchical": "true"},
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["manual"] == "給付金編"
    assert isinstance(data["toc"], list)
    assert len(data["toc"]) > 0

    first = data["toc"][0]
    # フラット版と同じ最低限のキー
    assert "id" in first
    assert "title" in first
    # children が存在するなら、None か list のどちらかを許容する
    if "children" in first:
        assert first["children"] is None or isinstance(first["children"], list)

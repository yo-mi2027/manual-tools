from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_text_hit_loose():
    """
    loose モードで、帝王切開が少なくとも1件ヒットすることを確認。
    OCRの空白混入などをまたいでヒットしていればOK。
    """
    resp = client.post(
        "/search_text",
        json={
            "manual_name": "給付金編",
            "query": "帝王切開",
            "mode": "loose",
            "limit": 5,
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0

    first = data["results"][0]
    assert "section_id" in first
    assert "snippet" in first
    assert isinstance(first["snippet"], str)
    assert len(first["snippet"]) > 0


def test_search_text_no_hit():
    """
    まず存在しないであろうクエリで 0 件になることを確認。
    """
    resp = client.post(
        "/search_text",
        json={
            "manual_name": "給付金編",
            "query": "絶対ヒットしないキーワードXYZ123",
            "mode": "plain",
            "limit": 5,
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0


def test_search_text_invalid_regex_fallback():
    """
    不正な正規表現パターンを渡しても 500 にならず、プレーン一致にフォールバックすることを確認。
    ヒット件数は 0 でも 1 でもよく、重要なのは 200 で落ちないこと。
    """
    resp = client.post(
        "/search_text",
        json={
            "manual_name": "給付金編",
            "query": "(",
            "mode": "regex",
            "limit": 3,
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)

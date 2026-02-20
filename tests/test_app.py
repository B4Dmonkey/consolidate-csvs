from app import consolidate


def test_consolidate():
    assert "hello world" in consolidate([])

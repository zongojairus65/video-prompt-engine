from core.cache import PromptCache


def test_cache_set_and_get():
    cache = PromptCache()

    value = {"result": "test"}

    cache.set("hello", "veo", value)

    assert cache.get("hello", "veo") == value


def test_cache_separates_generators():
    cache = PromptCache()

    cache.set("hello", "veo", {"generator": "veo"})

    assert cache.get("hello", "veo") is not None
    assert cache.get("hello", "kling") is None


def test_cache_clear():
    cache = PromptCache()

    cache.set("hello", "veo", {"result": "test"})
    cache.clear()

    assert cache.get("hello", "veo") is None

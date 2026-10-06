_client = None


def set_client(client):
    global _client
    _client = client


def get_client():
    if _client is None:
        raise RuntimeError(
            "pyLiveMusic server has not been initialized. "
            "Create Client() first."
        )

    return _client
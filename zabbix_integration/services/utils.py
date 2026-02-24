from datetime import datetime, timezone


def dt_from_epoch(epoch):
    if not epoch:
        return None
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc)


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]
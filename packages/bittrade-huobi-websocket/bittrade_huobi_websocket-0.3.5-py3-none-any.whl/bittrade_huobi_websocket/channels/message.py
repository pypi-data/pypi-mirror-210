def make_sub_unsub_messages(channel: str):
    return {"action": "sub", "ch": channel}, {"action": "unsub", "ch": channel}

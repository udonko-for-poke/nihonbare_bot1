def lookup_ev(ev_name, _list):
    for i, x in enumerate(_list):
        if (len(x) > 0 and ev_name == x[1]):
            return i
    else:
        return -1

def lookup_ev2(mes_id, _list):
    for i, x in enumerate(_list):
        if (len(x) > 0 and mes_id == x[0]):
            return i
    else:
        return -1

async def get_players(event_id, channel):
    msg = await channel.fetch_message(event_id)
    reactions = msg.reactions
    players = set()
    for reaction in reactions:
        async for user in reaction.users():
            players.add(user)
    return players
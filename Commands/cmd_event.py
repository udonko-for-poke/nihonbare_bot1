def lookup_ev(id_name, _list):
    for i, x in enumerate(_list):
        if id_name in x:
            return i
    else:
        return -1

async def get_players(event_id, channel):
    msg = await channel.fetch_message(event_id)
    reactions = msg.reactions
    players = set()
    for reaction in reactions:
        async for user in reaction.users():
            players.add(user.name)
    return list(players)
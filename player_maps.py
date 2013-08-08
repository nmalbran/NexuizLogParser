
BOTS = {
    '[BOT]Airhead':      ['[BOT]Airhead'],
    '[BOT]Death':        ['[BOT]Death'],
    '[BOT]Delirium':     ['[BOT]Delirium'],
    '[BOT]Discovery':    ['[BOT]Discovery'],
    '[BOT]Dominator':    ['[BOT]Dominator'],
    '[BOT]Eureka':       ['[BOT]Eureka'],
    '[BOT]Gator':        ['[BOT]Gator'],
    '[BOT]Hellfire':     ['[BOT]Hellfire'],
    '[BOT]Lion':         ['[BOT]Lion'],
    '[BOT]Mystery':      ['[BOT]Mystery'],
    '[BOT]Necrotic':     ['[BOT]Necrotic'],
    '[BOT]Pegasus':      ['[BOT]Pegasus'],
    '[BOT]Resurrection': ['[BOT]Resurrection'],
    '[BOT]Scorcher':     ['[BOT]Scorcher'],
    '[BOT]Sensible':     ['[BOT]Sensible'],
    '[BOT]Shadow':       ['[BOT]Shadow'],
    '[BOT]Shadow':       ['[BOT]Shadow'],
    '[BOT]Thunderstorm': ['[BOT]Thunderstorm'],
    '[BOT]Toxic':        ['[BOT]Toxic']
}


class KnownPlayerMapAdmin(object):

    def __init__(self, known_player_nicks):
        self.known_player_nicks = dict(BOTS, **known_player_nicks)
        self.info = []
        self.all_nicks = set()

    def get_name_from_nick(self, nick):
        for name in self.known_player_nicks:
            if nick in self.known_player_nicks[name]:
                return name

        if nick not in self.all_nicks:
            self.all_nicks.add(nick)
            self.info.append("Nick not recognized: '%s': ['%s']" % (nick, repr(nick)))
        return 'UNKNOWN'

    def get_map(self):
        return self.known_player_nicks

    def get_info(self):
        return self.info


class EmptyPlayerMapAdmin(object):

    def __init__(self):
        self.known_player_nicks = BOTS
        self.info = []
        self.all_nicks = set()
        self.n = 0

    def _get_new_name(self):
        name = 'player_%d' % self.n
        self.n += 1
        return name

    def get_name_from_nick(self, nick):
        for name in self.known_player_nicks:
            if nick in self.known_player_nicks[name]:
                return name

        if nick not in self.all_nicks:
            self.all_nicks.add(nick)
            name = self._get_new_name()
            self.known_player_nicks[name] = [nick]
            return name

        return "UNKNOWN"

    def get_map(self):
        return self.known_player_nicks

    def get_info(self):
        return self.info

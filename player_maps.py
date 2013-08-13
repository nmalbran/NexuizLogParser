
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
BOT_PREFIX = '[BOT]'


class PlayerMapAdmin(object):

    def __init__(self):
        self.known_player_nicks = BOTS
        self.info = []
        self.all_nicks = set()

    def is_bot(self, name):
        return name.startswith(BOT_PREFIX)

    def get_name_from_nick(self, nick):
        for name in self.known_player_nicks:
            if nick in self.known_player_nicks[name]:
                return name
        return None

    def get_map(self):
        return self.known_player_nicks

    def get_info(self):
        return self.info


class KnownPlayerMapAdmin(PlayerMapAdmin):

    def __init__(self, known_player_nicks):
        super(KnownPlayerMapAdmin, self).__init__()
        self.known_player_nicks = dict(self.known_player_nicks, **known_player_nicks)

    def get_name_from_nick(self, nick):
        name = super(KnownPlayerMapAdmin, self).get_name_from_nick(nick)
        if name:
            return name

        if nick not in self.all_nicks:
            self.all_nicks.add(nick)
            self.info.append("Nick not recognized: '%s': ['%s']" % (nick, repr(nick)))
        return 'UNKNOWN'


class EmptyPlayerMapAdmin(PlayerMapAdmin):

    def get_name_from_nick(self, nick):
        name = super(EmptyPlayerMapAdmin, self).get_name_from_nick(nick)
        if name:
            return name

        if nick not in self.all_nicks:
            self.all_nicks.add(nick)
            self.known_player_nicks[nick] = [nick]
            return nick

        return "UNKNOWN"


class AutoCompletePlayerMapAdmin(PlayerMapAdmin):

    def __init__(self, extra_nicks):
        super(AutoCompletePlayerMapAdmin, self).__init__()
        self.known_player_nicks = dict(self.known_player_nicks, **extra_nicks)

    def get_name_from_nick(self, nick):
        name = super(AutoCompletePlayerMapAdmin, self).get_name_from_nick(nick)
        if name:
            return name

        if nick not in self.all_nicks:
            self.all_nicks.add(nick)
            self.info.append("Nick not recognized: '%s': ['%s']" % (nick, repr(nick)))
            self.known_player_nicks[nick] = [nick]
            return nick

        return 'UNKNOWN'
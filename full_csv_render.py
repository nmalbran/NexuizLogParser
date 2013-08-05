
import sys
from players import KNOWN_PLAYER_NICKS
from weapons import WEAPONS
from nex_parser import NexuizLogParser

class FullCSVRender():

    def __init__(self, players):
        self.all_players = KNOWN_PLAYER_NICKS.keys()
        self.all_weapons = WEAPONS.values()
        self.players = players

    def is_bot(self, name):
        return name.startswith('[BOT]')

    def output(self):
        self._flatten_players()
        self._clean_keys()

        players = self.players.values()
        all_keys = sorted(players[0].keys())

        output = "%s\n" % ','.join(all_keys)

        for p in players:
            if self.is_bot(p['name']):
                continue
            line = ''
            for key in all_keys:
                val = p[key]
                if type(val) is str:
                    line += '"%s",' % val
                else:
                    line += '%s,' % val
            output += line[:-1] + "\n"

        return output

    def _flatten_players(self):
        for pname in self.players:
            for p in self.all_players:
                self.players[pname]["kills_by_%s" % p] = self.players[pname]['kills_by_player'].get(p, 0)
                self.players[pname]["deaths_by_%s" % p] = self.players[pname]['deaths_by_player'].get(p, 0)

            for w in self.all_weapons:
                self.players[pname]["kills_by_%s" % w] = self.players[pname]['kills_by_weapon'].get(w, 0)

            del self.players[pname]['kills_by_player']
            del self.players[pname]['deaths_by_player']
            del self.players[pname]['kills_by_weapon']

    def _clean_keys(self):
        delete_keys = ['team', 'nemesis', 'rag_doll', 'pweapon', 'deaths_by_Unknown']
        for pname in self.players:
            for key in delete_keys:
                del self.players[pname][key]



if __name__ == '__main__':

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log(sys.argv[1:])

    average = nlp.get_average()
    fcr = FullCSVRender(average)

    print fcr.output()


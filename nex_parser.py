# -*- coding: utf-8 -*-

from datetime import datetime
from optparse import OptionParser
from weapons import WEAPONS, WEAPON_MOD

TEAM_COLOR = {'5': 'Red', '14': 'Blue'}
SEP = "=" * 80


class NexuizLogParser:

    def __init__(self, known_player_nicks, teams=TEAM_COLOR):
        self.reset()
        self.known_player_nicks = known_player_nicks
        self.teams = teams

        self.longest_name_length_bot = max([len(p) for p in known_player_nicks.keys()])
        self.longest_name_length = max([len(p) for p in known_player_nicks.keys() if not self.is_bot(p)])
        fcl = str(max(self.longest_name_length, 4) + 1)
        fcl_bot = str(max(self.longest_name_length_bot, 4) + 1)

        STR_FORMAT_BASE = ["%(name)", "s  %(frags)5s  %(suicide)8s  %(accident)9s  %(tk)10s  %(deaths)6s  %(steal)6s  %(capture)4s  %(pickup)7s  %(teams)s"]

        self.str_format = STR_FORMAT_BASE[0] + fcl + STR_FORMAT_BASE[1]
        self.str_format_bot = STR_FORMAT_BASE[0] + fcl_bot + STR_FORMAT_BASE[1]


    def reset(self):
        """
            Reset variables for a new log file.
        """
        self.in_game = False
        self.count = 0
        self.line_number = 0
        self.games = dict()
        self.player_nicks = set()
        self.info = []
        self.total = dict()


    def is_bot(self, name):
        return name.startswith('[BOT]')


    def _get_name_from_nick(self, nick):
        for name in self.known_player_nicks:
            if nick in self.known_player_nicks[name]:
                return name
        if nick not in self.player_nicks:
            self.player_nicks.add(nick)
            self.info.append("Nick not recognized (line: %d): '%s': ['%s']" % (self.line_number, nick, repr(nick)))
        return 'UNKNOWN'


    def get_results(self):
        """
            Return a dictionary with all the parsed information.
        """
        return self.games


    def get_total(self):
        """
            Return a dictionary with summary of all games in the log.
        """
        return self.total


    def parse_log(self, logfile):
        """
            Parse the log in `logfile`.
        """
        for line in open(logfile):
            self.line_number += 1

            if (len(line) > 25) and (line[24] == ":"):
                timestamp = line[3:22]
                gametime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                command = line[25:].strip().split(":")

                ########################
                # COMAND PARSING START #
                ########################
                command_name = command[0]
                if command_name == "gamestart":
                    underscore_pos = command[1].find('_')
                    game_type = command[1][:underscore_pos]
                    map_name = command[1][underscore_pos+1:]

                    self.in_game = True
                    self.games[self.count] = dict()
                    self.games[self.count]['map_data'] = {'map_name': map_name,
                                                          'start_time': gametime,
                                                          'duration': '',
                                                          'game_type': game_type,
                                                          }

                    self.games[self.count]['teams'] = dict()
                    for (t_id, team) in self.teams.items():
                        self.games[self.count]['teams'][t_id] = {'id': t_id, 'color': team, 'caps': 0, 'score': 0}

                elif not self.in_game:
                    # commands outside a game are discarded
                    continue

                elif command_name == "gameinfo":
                    subcommand = command[1]
                    if subcommand == "end":
                        pass
                    elif subcommand == "mutators":
                        mutators = command[2:]
                    else:
                        # just to discover other gameinfo log lines
                        self.info.append('gameinfo subcommand not recognized (line %d):' % line_number)
                        self.info.append(command)

                elif command_name == "scores":
                    pass

                elif command_name == "join":
                    # This data is valid only during this game
                    # ip_from: IP address of the player
                    # nick: Nickname of the player
                    # xx: ??
                    player_id, xx, ip_from, nick = command[1:]
                    #if nick[0:5] != "[BOT]":
                    player_name = self._get_name_from_nick(nick)

                    if 'players' not in self.games[self.count]:
                        self.games[self.count]['players'] = dict()

                    if player_id not in self.games[self.count]['players']:
                        self.games[self.count]['players'][player_id] = {
                                                                        'id': player_id,
                                                                        'ip': ip_from,
                                                                        'nick': nick,
                                                                        'name': player_name,

                                                                        'team': [],

                                                                        'frags': 0,
                                                                        'suicide': 0,
                                                                        'accident': 0,
                                                                        'tk': 0,
                                                                        'deaths': 0,

                                                                        'kills_by_player': dict(),
                                                                        'deaths_by_player': dict(),

                                                                        'capture': 0,
                                                                        'return': 0,
                                                                        'steal': 0,
                                                                        'dropped': 0,
                                                                        'pickup': 0,}



                elif command_name == "team":
                    player_id , team_id = command[1:]
                    change_time = gametime - self.games[self.count]['map_data']['start_time']
                    if team_id not in self.teams:
                        continue
                    self.games[self.count]['players'][player_id]['team'].append("%s (%s)" % (self.teams[team_id], change_time))

                elif command_name == "kill":
                    text, killer, killed = command[1:4]
                    other_data = command[4:] # items=killer weapon, victimitems=killed weapon
                    self.games[self.count]['players'][killed]['deaths'] += 1

                    # killer_weapon = other_data[1][6:]
                    # killer_weapon_id = ''
                    # killer_weapon_mod = ''
                    # for c in killer_weapon:
                    #     try:
                    #         int(c)
                    #         killer_weapon_id += c
                    #     except ValueError as e:
                    #         killer_weapon_mod += c

                    # if killer_weapon_id not in WEAPONS:
                    #     print self.line_number, str(killer_weapon)

                    # for m in killer_weapon_mod:
                    #     if m not in WEAPON_MOD:
                    #         print self.line_number, str(killer_weapon)

                    if text == "frag":         # kill other player
                        self.games[self.count]['players'][killer]['frags'] += 1
                        self.games[self.count]['players'][killer]['kills_by_player'][killed] = self.games[self.count]['players'][killer]['kills_by_player'].get(killed, 0) + 1
                        self.games[self.count]['players'][killed]['deaths_by_player'][killer] = self.games[self.count]['players'][killed]['deaths_by_player'].get(killer, 0) + 1

                    elif text == "suicide":    # kill himself, by weapon
                        self.games[self.count]['players'][killer]['suicide'] += 1
                    elif text == "accident":   # kill himself, not by weapon
                        self.games[self.count]['players'][killer]['accident'] += 1
                    elif text == "tk":         # TeamMate kill
                        self.games[self.count]['players'][killer]['tk'] += 1
                    else:
                        self.info.append('kill text not recognized for command (line %d):' % self.line_number)
                        self.info.append(command)

                elif command_name == "ctf":
                    # Recognized subcommand:
                    #  returned --> lost flag automatically returned by timeout
                    #  capture  --> a capture for the team
                    #  return   --> flag returned by a player
                    #  steal    --> flag stealed by a player (flag in the base)
                    #  dropped  --> flag dropped by the player
                    #  pickup   --> flag taken by a player (flag in the field)
                    subcommand = command[1]
                    team_id = command[2]
                    if subcommand == "returned":
                        pass
                    elif (subcommand == "capture" or
                         subcommand == "return"  or
                         subcommand == "steal"   or
                         subcommand == "dropped" or
                         subcommand == "pickup"):
                        player_id = command[3]
                        self.games[self.count]['players'][player_id][subcommand] += 1
                    else:
                        self.info.append('ctf subcommand not recognized (line %d):' % self.line_number)
                        self.info.append(command)

                elif command_name == "part":
                    # This means: "player_id left the game"
                    player_id = command[1]

                elif command_name == "labels":
                    subcommand = command[1]
                    if subcommand == "player":
                        pass
                    elif subcommand == "teamscores":
                        pass
                    else:
                        self.info.append('labels subcommand not recognized (line %d):' % self.line_number)
                        self.info.append(command)

                elif command_name == "player":
                    # final stats for player
                    player_stats = command[2:]

                elif command_name == "teamscores":
                    # final stats for teams
                    team_stats = command[2]
                    team_id = command[3]
                    if team_id in self.teams and team_stats:
                        caps, score = team_stats.split(',')
                        self.games[self.count]['teams'][team_id]['caps'] = int(caps)
                        self.games[self.count]['teams'][team_id]['score'] = int(score)

                elif command_name == "end":
                    self.games[self.count]['map_data']['end_time'] = gametime
                    self.games[self.count]['map_data']['duration'] = str(gametime - self.games[self.count]['map_data']['start_time'])

                elif command_name == "gameover":
                    # This command marks the end of the game
                    self.count += 1
                    self.in_game = False
                    #break # for testing only... I want to play with 1 game's data

                elif command_name == "vote":
                    # This command shows map voting
                    subcommand = command[1]
                    if subcommand == "keeptwo":
                        pass
                    elif subcommand == "finished":
                        pass

                elif command_name == "recordset":
                    pass

                elif command_name == "name":
                    # Player changes his/her name
                    pass

                else:
                    # This is to show any unknown command
                    self.info.append('main command not recognized (line %d):' % line_number)
                    self.info.append(command)

        self._compute_total()

    def _compute_total(self):
        stats = ['frags', 'suicide', 'accident', 'tk', 'deaths', 'capture', 'return', 'steal', 'dropped', 'pickup']
        stats_by_player = ['kills_by_player', 'deaths_by_player']
        for game in self.games.values():
            if 'players' not in game:
                continue
            players = game['players'].values()
            players_id = dict([(p['id'], p['name']) for p in players])

            for player in players:
                pname = player['name']
                if pname not in self.total:
                    self.total[pname] = {'name': pname, 'team': []}

                for stat in stats:
                    self.total[pname][stat] = self.total[pname].get(stat, 0) + player[stat]

                for stat in stats_by_player:
                    if stat not in self.total[pname]:
                        self.total[pname][stat] = dict()

                    for pid, num in player[stat].items():
                        self.total[pname][stat][players_id[pid]] = self.total[pname][stat].get(players_id[pid], 0) + num


    def display_games_scores(self, display_bot=False):
        """
            Display the results of the parsed log file.
            @display_bot: if set, it display bot results.
        """
        for (game_id, game) in self.games.items():
            self.display_game_scores(game, display_bot)


    def display_game_scores(self, game, display_bot=False):
        print SEP
        print " MAP: %s  TYPE: %s  DATE: %s  DURATION: %s" % (game['map_data']['map_name'], game['map_data']['game_type'], game['map_data']['start_time'], game['map_data']['duration'])
        print SEP
        if 'players' in game:
            self._display_players_scores(game['players'], display_bot)
            self.display_kills_by_player(game['players'], display_bot)
        else:
            print 'No Players'

        if 'teams' in game and game['map_data']['game_type'] == 'ctf':
            self._display_teams_scores(game['teams'])
        print SEP


    def _display_players_scores(self, players, display_bot=False):
        strf = self.str_format_bot if display_bot else self.str_format
        print strf % {'name': 'NICK',
                      'frags': 'FRAGS',
                      'suicide': 'SUICIDES',
                      'accident': 'ACCIDENTS',
                      'tk': 'TEAM KILL',
                      'deaths': 'DEATHS',
                      'capture': 'CAPS',
                      'steal': 'STEALS',
                      'pickup': 'PICKUPS',
                      'teams': 'TEAM'}
        for player in sorted(players.values(), key= lambda x: x['name']):
            self._display_player_scores(player, display_bot)


    def _display_player_scores(self, player, display_bot=False):
        if self.is_bot(player['name']) and not display_bot:
            return
        player['teams'] = ', '.join(player['team'])

        strf = self.str_format_bot if display_bot else self.str_format
        print strf % player


    def _display_teams_scores(self, teams):
        print "\n   TEAMS  CAPS  SCORES"
        for t_id, team in teams.items():
            print "   %(color)5s  %(caps)4s  %(score)s" % team


    def display_parser_info(self):
        """
            Display info messages generated by the parser.
        """
        if not self.info:
            return
        print "\nPARSER INFO:"
        for e in self.info:
            print e


    def display_kills_by_player(self, game_players, display_bot=False):
        players = dict()
        for p_id, p in game_players.items():
            if not display_bot and self.is_bot(p['name']):
                continue
            players[p_id] = p['name']

        order = sorted(players.keys())

        cwidth = self.longest_name_length_bot if display_bot else self.longest_name_length
        strf = ("  %"+str(cwidth)+"s") * (len(players)+1)

        print ""
        print strf % tuple(['KILLER']+[players[p] for p in order])
        for killer in order:
            line = [players[killer]]
            for killed in order:
                line.append(game_players[killer]['kills_by_player'].get(killed, 0))
            print strf % tuple(line)
        print ""


    def display_total(self, display_bot=False):
        print SEP
        print "   TOTAL  N° JUEGOS: %s" % len(self.games)
        print SEP
        self._display_players_scores(self.total, display_bot)
        self.display_kills_by_player(self.total, display_bot)
        print SEP


if __name__ == '__main__':
    from players import KNOWN_PLAYER_NICKS

    parser = OptionParser()
    parser.add_option('-b', "--bot", action="store_true", help="Display Bot's results [False]", default=False)
    parser.add_option("--nototal", action="store_false", dest='total', help="Don't display totals", default=True)
    parser.add_option("--noparcial", action="store_false", dest='parcial', help="Don't display individual game results", default=True)
    (options, args) = parser.parse_args()

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log(args[0])
    if options.parcial:
        nlp.display_games_scores(display_bot=options.bot)
    if options.total:
        nlp.display_total(display_bot=options.bot)
    nlp.display_parser_info()

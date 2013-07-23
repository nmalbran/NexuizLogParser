# -*- coding: utf-8 -*-

from datetime import datetime
TEAM_COLOR = {'5': 'Red', '14': 'Blue'}

class NexuizLogParser:

    def __init__(self, known_player_nicks, teams=TEAM_COLOR):
        self.reset()
        self.known_player_nicks = known_player_nicks
        self.teams = teams

        longest_name_length_bot = max([len(p) for p in known_player_nicks.keys()])
        longest_name_length = max([len(p) for p in known_player_nicks.keys() if not self.is_bot(p)])
        fcl = str(max(longest_name_length, 4) + 1)
        fcl_bot = str(max(longest_name_length_bot, 4) + 1)
        self.STR_FORMAT = "%(name)"+ fcl + "s  %(frags)5s  %(suicide)8s  %(accident)9s  %(tk)3s  %(steal)6s  %(capture)4s  %(pickup)7s  %(teams)s"
        self.STR_FORMAT_BOT = "%(name)"+ fcl_bot + "s  %(frags)5s  %(suicide)8s  %(accident)9s  %(tk)3s  %(steal)6s  %(capture)4s  %(pickup)7s  %(teams)s"


    def reset(self):
        """
            Reset variables for a new log file.
        """
        self.in_game = False
        self.count = 0
        self.line_number = 0
        self.games = dict()
        self.game_type = 'ctf'
        self.player_nicks = set()
        self.info = []


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


    def parse_log(self, logfile):
        """
            Parse the log in `logfile`.
        """
        for line in open(logfile):
            self.line_number += 1

            if line[24:58] == 'Game type successfully switched to':
                self.game_type = line[58:].strip()

            if (len(line) > 25) and (line[24] == ":"):
                timestamp = line[3:22]
                gametime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                command = line[25:].strip().split(":")

                ########################
                # COMAND PARSING START #
                ########################
                command_name = command[0]
                if command_name == "gamestart":
                    self.in_game = True
                    self.games[self.count] = dict()
                    self.games[self.count]['map_data'] = {'map_name': command[1],
                                                          'start_time': gametime,
                                                          'duration': '',
                                                          'game_type': self.game_type,
                                                          }

                    self.games[self.count]['teams'] = dict()
                    for (t_id, team) in self.teams.items():
                        self.games[self.count]['teams'][t_id] = {'id': t_id, 'color': team, 'caps': '0', 'score': '0'}

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
                    if text == "frag":         # kill other player
                        self.games[self.count]['players'][killer]['frags'] += 1
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
                        self.games[self.count]['teams'][team_id]['caps'] = caps
                        self.games[self.count]['teams'][team_id]['score'] = score

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


    def display_games_scores(self, display_bot=False):
        """
            Display the results of the parsed log file.
            @display_bot: if set, it display bot results.
        """
        for (game_id, game) in self.games.items():
            self._display_game_scores(game, display_bot)


    def _display_game_scores(self, game, display_bot=False):
        sep = "=" * 80
        print sep
        print " MAP: %s  TYPE: %s  DATE: %s  DURATION: %s" % (game['map_data']['map_name'], game['map_data']['game_type'], game['map_data']['start_time'], game['map_data']['duration'])
        print sep
        if 'players' in game:
            self._display_players_scores(game['players'], display_bot)
        else:
            print 'No Players'

        if 'teams' in game and game['map_data']['game_type'] == 'ctf':
            self._display_teams_scores(game['teams'])
        print sep


    def _display_players_scores(self, players, display_bot=False):
        strf = self.STR_FORMAT_BOT if display_bot else self.STR_FORMAT
        print strf % {'name': 'NICK',
                      'frags': 'FRAGS',
                      'suicide': 'SUICIDES',
                      'accident': 'ACCIDENTS',
                      'tk': 'TK',
                      'capture': 'CAPS',
                      'steal': 'STEALS',
                      'pickup': 'PICKUPS',
                      'teams': 'TEAM'}
        for (player_id, player) in players.items():
            self._display_player_scores(player, display_bot)


    def _display_player_scores(self, player, display_bot=False):
        if self.is_bot(player['name']) and not display_bot:
            return
        player['teams'] = ', '.join(player['team'])

        strf = self.STR_FORMAT_BOT if display_bot else self.STR_FORMAT
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


if __name__ == '__main__':
    import sys
    from players import KNOWN_PLAYER_NICKS

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log(sys.argv[1])
    nlp.display_games_scores(display_bot=False)
    nlp.display_parser_info()

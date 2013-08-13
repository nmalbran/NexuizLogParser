Nexuiz Log Parser
=================

Log parser for Nexuiz game.
Based in Trablas' parser.

### Installation

    python setup.py install

### Usage example

#### CLI
    nexlogparser server.log
    nexlogparser -t txt server.log
    nexlogparser *.log -o all.html

    Usage: nexlogparser [options] logfile1 [logfile2 logfile3 ...]
    Options:
      -h, --help            show this help message and exit
      -t TYPE, --type=TYPE  Type of the output result (html, txt)
      -o OUTPUT, --output=OUTPUT
                            File to output result.
      -b, --bot             Display Bot's results
      -p PLAYERS, --players=PLAYERS
                            Package.variable containing the players/nicks map.
                            Default: players.PLAYERS
      --nototal             Don't display totals
      --noparcial           Don't display individual game results
      -q, --quiet           Don't display parser error


#### As module
    from nexuiz_log_parser import NexuizLogParser

    nlp = NexuizLogParser(PLAYERS)
    nlp.parse_logs(['server.log'])

    print nlp.get_results()

### `PLAYERS` format
The same person can have different nicknames in one log file. To solve that, the parser receive the following dictionary with nicknames:

    PLAYERS =
        {
            'NamePlayer1': ['nick1', 'nick2', 'nick3'],
            'NamePlayer2': ['John', 'foo', 'bar'],
        }

`PLAYERS` can be an empty dict and players name will be auto generated.

The option `-p, --players` is used to point where to find the dict:

- `-p foo.bar` => `from foo import bar as PLAYERS`
- `-p foo` => `from foo import PLAYERS`
- no `-p` => `from players import PLAYERS`
- if the above fails => `PLAYERS = dict()`


### Result format
The results given by the `NexuizLogParser.get_results()` and `NexuizLogParser.get_total()` functions follow this format:

    get_results() = {
                     0: {
                         'map_data': {
                                      'map_name': string,
                                      'start_time': datetime.datetime,
                                      'end_time': datetime.datetime,
                                      'duration': 'H:MM:SS',
                                      'game_type': string,
                         },
                         'teams': {
                                   team1_color: {
                                                 'id': int,
                                                 'color': string,
                                                 'caps': int,
                                                 'score': int,
                                                 'last_players': str,
                                                 'captures_log': [(time,  player_name), ...],
                                   },
                                   team2_color: {...},
                         },
                         'players': {
                                     player1_name: {
                                                  'id': int,
                                                  'ip': string,
                                                  'nick': string,
                                                  'name': string,
                                                  'team': ['<team_color> (H:MM:SS)', ...],
                                                  'last_team': str,

                                                  'frags': int,
                                                  'fc_kills': int,
                                                  'sc_kills': int,
                                                  'ic_kills': int,
                                                  'tc_kills': int,

                                                  'kills_wf': int,
                                                  'kills_ws': int,
                                                  'kills_wi': int,

                                                  'tk': int,
                                                  'deaths': int,
                                                  'suicide': int,
                                                  'accident': int,

                                                  'killing_spree': [int, int, ...],
                                                  'n_killing_spree': int,
                                                  'max_killing_spree': int,

                                                  'kills_by_player': {
                                                                      player1_name: int,
                                                                      player2_name: int,
                                                  },
                                                  'deaths_by_player': {
                                                                      player1_name: int,
                                                                      player2_name: int,
                                                  },
                                                  'kills_by_weapon': {
                                                                      weapon_name1: int,
                                                                      weapon_name2: int,
                                                  },

                                                  'capture': int,
                                                  'return': int,
                                                  'steal': int,
                                                  'dropped': int,
                                                  'pickup': int,

                                                  'pweapon': str,
                                                  'survival_index': float,
                                                  'cap_index': float %,
                                                  'nemesis': str,
                                                  'rag_doll': str,
                                     },
                                     player2_name: {...},
                         }
                     },
                     1: {...},
                    }

    get_average()
    get_total() = {
                   player1_name: {
                                  'name': string,
                                  'team': [],

                                  'frags': int,
                                  'fc_kills': int,
                                  'sc_kills': int,
                                  'ic_kills': int,
                                  'tc_kills': int,

                                  'kills_wf': int,
                                  'kills_ws': int,
                                  'kills_wi': int,
                                  'tk': int,
                                  'deaths': int,
                                  'suicide': int,
                                  'accident': int,

                                  'n_killing_spree': int,
                                  'max_killing_spree': int,

                                  'kills_by_player': {
                                                      player1_name: int,
                                                      player2_name: int,
                                  },
                                  'deaths_by_player': {
                                                      player1_name: int,
                                                      player2_name: int,
                                  },
                                  'kills_by_weapon': {
                                                      weapon_name1: int,
                                                      weapon_name2: int,
                                  },

                                  'capture': int,
                                  'return': int,
                                  'steal': int,
                                  'dropped': int,
                                  'pickup': int,

                                  'pweapon': str,
                                  'survival_index': float,
                                  'cap_index': float %,
                                  'nemesis': str,
                                  'rag_doll': str,

                                  'games_played': int,
                   },
                   player2_name: {...},
                  }

*Notes*:

- `player.id` and `team.id` are the id given by Nexuiz, in string format.
- `players.nick` is the nickname used in that game, while `players.name` is the name mapped by `PLAYERS`.
- The time in `players.team` is when the player joined the team.
- The top level numbers are the game's number, in order of appearance in the log.
- `player.last_team` is the last team which the player joined.
- `team.last_players` are the players according to `player.last_team`

### Stats definition

- `pweapon`: The name of the weapon used to kill the most
- `survival_index`: `frags / deaths`
- `cap_index`: `capture *100 / (steal + pickup)`%
- `nemesis`: The name of the player who killed most times this player
- `rag_doll`: The name of the player killed most time by this player

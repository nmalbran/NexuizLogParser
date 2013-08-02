Nexuiz Log Parser
=================

Log parser for Nexuiz game.
Based in Trablas' parser.

### Usage example

#### CLI
    python nex_parser.py -t txt server.log
    python nex_parser.py -o stats.html server.log
    python nex_parser.py *.log -o all.html

    Usage: nex_parser.py [options] logfile1 [logfile2 logfile3 ...]
    Options:
      -h, --help            show this help message and exit
      -t TYPE, --type=TYPE  Type of the output result (html, txt)
      -o OUTPUT, --output=OUTPUT
                            File to output result.
      -b, --bot             Display Bot's results
      --nototal             Don't display totals
      --noparcial           Don't display individual game results
      -q, --quiet           Don't display parser error



#### As module
    from nex_parser import NexuizLogParser

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log('server.log')

    print nlp.get_results()

### `KNOWN_PLAYER_NICKS` format
The same person can have different nicknames in one log file. To solve that, the parser receive the following dictionary with nicknames:

    KNOWN_PLAYER_NICKS =
        {
            'NamePlayer1': ['nick1', 'nick2', 'nick3'],
            'NamePlayer2': ['John', 'foo', 'bar'],
        }

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
                                   team1_id: {
                                              'id': team1_id,
                                              'color': string,
                                              'caps': int,
                                              'score': int,
                                   },
                                   team2_id: {...},
                         },
                         'players': {
                                     player1_name: {
                                                  'id': int,
                                                  'ip': string,
                                                  'nick': string,
                                                  'name': string,
                                                  'team': ['<team_color> (H:MM:SS)', ...],

                                                  'frags': int,
                                                  'fckills': int,
                                                  'tk': int,
                                                  'deaths': int,
                                                  'suicide': int,
                                                  'accident': int,

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

    get_total() = {
                   player1_name: {
                                  'name': string,
                                  'team': [],

                                  'frags': int,
                                  'fckills': int,
                                  'tk': int,
                                  'deaths': int,
                                  'suicide': int,
                                  'accident': int,

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

- `teamX_id` is the id given by Nexuiz, in string format.
- `[]['players']['nick']` is the nickname used in that game, while `[]['players']['name']` is the name mapped by `KNOWN_PLAYER_NICKS`.
- The time in `[]['players']['team']` is when the player joined the team.
- The top level numbers are the game's number, in order of appearance in the log.

### Stats definition

- `pweapon`: The name of the weapon used to kill the most
- `survival_index`: `frags / deaths`
- `cap_index`: `capture *100 / (steal + pickup)`%
- `nemesis`: The name of the player who killed most times this player
- `rag_doll`: The name of the player killed most time by this player

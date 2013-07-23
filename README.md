Nexuiz Log Parser
=================

Log parser for Nexuiz game.
Based in Trablas' parser.

### Usage example

#### CLI
    python nex_parser.py server.log

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

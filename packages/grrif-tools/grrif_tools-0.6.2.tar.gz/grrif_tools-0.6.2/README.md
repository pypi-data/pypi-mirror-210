# GRRIF Tools

A set of tools for Cool Cats™. Allows you to archive GRRIF's play history to a SQLite database (or text files), compute/display some stats (top 10/25/100 artists and tracks), ~~and scrobble it to last.fm~~ (upcoming).

```
usage: grrif_tools [-h] {archive,stats,scrobble} ...

A set of tools for Cool Cats™. Allows you to archive GRRIF's play history and scrobble it to last.fm (upcoming).

positional arguments:
  {archive,stats,scrobble}
    archive             Archive GRRIF's play history.
    stats               Get some stats out of the database.
    scrobble            Scrobble to Last.fm.

options:
  -h, --help            show this help message and exit
  ```
  
  **NOTE:** This package is unofficial and meant mostly as a playground to experiment with some new things (argparse, python packaging, etc...). Please do not DDoS GRRIF's website !

# tvdbAPI
This is an API library for use when connecting to The TVDB.

## How to Use
```
from tvdbAPI import TVDB

t = TVDB()

# Get basic info about a show
t.getShow("Mythbusters")

# Get a list of all episodes of a show
t.getEpisodes("Mythbusters")

# Get a specific episodes name
t.getEpisodeName("Scrubs", 1, 1)
```
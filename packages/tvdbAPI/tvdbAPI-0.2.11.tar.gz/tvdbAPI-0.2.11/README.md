# tvdbAPI
This is an API library for use when connecting to The TVDB.

# How to Use
## Import Package
```
from tvdbAPI import TVDB
```
## Use the Module
```
t = TVDB()
```
## Get Basic Info About a Given Show
```
"""Gets basic info about the show with given 'name'.

Arguments:
    name {String} -- The name of the show you are searching for.

Raises:
    InvalidInput: Raises if a non string is entered for name.
    ShowNotFound: Raises if no show was found for the given name/alias.

Returns:
    dict -- Returns a dictionary containg basic data about the show.
"""
t.getShow("Mythbusters")
```

## Get a List of all Episodes of a Given Show
```
"""Gets a list of all the episodes for a given show.

Arguments:
    name {String} -- The name of the show being searched for.

Keyword Arguments:
    accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})

Raises:
    InvalidInput: Raises if a non string is inputed for name.
    InvalidShowID: Raises if a show was not found.

Returns:
    list -- Returns a list of all the episodes for a given show.
"""
t.getEpisodes("Mythbusters", 0.8)
```
## Get a Specific Episode's Name
```
"""Gets an episode by its name, based on the show name, season number, and episode number, and cleaned of any special characters so it can be used to name files without error.

Arguments:
    name {String} -- The name of the show being searched for.
    seasonNum {integer} -- The season number which the episode is in.
    epNum {integer} -- The episode number in the season.

Keyword Arguments:
    order {String} -- Specifies the episode number ordering to parse ("DVD", "Aired")
    accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
    id -- Optional input of show id when searching for episode names.

Raises:
    InvalidInput: Raises if a non string is inputed for name.
    InvalidShowID: Raises if a show was not found.

Returns:
    String -- Returns the name of the episode searched for, cleaned of all special characters.
"""
t.getEpisodeName("Scrubs", 1, 1, "Aired", 0.8)
```
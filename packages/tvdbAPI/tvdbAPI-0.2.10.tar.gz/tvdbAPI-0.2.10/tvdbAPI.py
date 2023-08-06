import requests
import sanction
from difflib import SequenceMatcher

# Exceptions


class Error(Exception):
    pass


class InvalidCredentials(Error):
    pass


class ShowNotFound(Error):
    pass


class NoSuchEpisode(Error):
    pass


class InvalidShowID(Error):
    pass


class InvalidInput(Error):
    pass


class NoActorsFound(Error):
    pass


class NoImagesFound(Error):
    pass

# Main TVDB object


class TVDB:

    def __init__(self, apikey='0C9MXRI7C0X5J1QH'):
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'en'
        }

        self.config = {}

        self.config['authPayload'] = {
            'apikey': '0C9MXRI7C0X5J1QH',
            'username': '',
            'userkey': ''
        }

        self.config['apiURL'] = "https://api.thetvdb.com"

        self.config['searchEndpoint'] = f"{self.config['apiURL']}/search/series"

        self.config['seriesEndpoint'] = f"{self.config['apiURL']}/series/"

        self.config['loginURL'] = f"{self.config['apiURL']}/login"

        self.config['imageURL'] = "https://thetvdb.com/banners/"

        self.__authorized = False

        self.session = requests.Session()

    def getShow(self, name):
        """ Gets basic info about the show with given 'name'.

        Arguments:
            name {String} -- The name of the show you are searching for.

        Raises:
            InvalidInput: Raises if a non string is entered for name.
            ShowNotFound: Raises if no show was found for the given name/alias.

        Returns:
            dict -- Returns a dictionary containg basic data about the show.
        """
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        params = {
            "name": name
        }
        r = self.session.get(
            self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise ShowNotFound("Show was not found, please try again")
        return r

    def getEpisodes(self, name, accuracy=0.8):
        """ Gets a list of all the episodes for a given show.

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
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name, accuracy)
        if id == -1:
            raise InvalidShowID("Show was not found, please try again")
        pages = self.session.get(
            self.config['seriesEndpoint'] + f"{id}/episodes", headers=self.headers).json()['links']['last']
        episodes = []
        for x in range(1, pages+1):
            params = {
                "page": x
            }
            data = self.session.get(
                self.config['seriesEndpoint'] + f"{id}/episodes", params=params, headers=self.headers).json()['data']
            for episode in data:
                episodes.append(episode)
        return episodes

    def getEpisodeName(self, name, seasonNum, epNum, order="", accuracy=0.8, id=None):
        """ Gets an episode by its name, based on the show name, season number, and episode number, and
            cleaned of any special characters so it can be used to name files without error.

        Arguments:
            name {String} -- The name of the show being searched for.
            seasonNum {integer} -- The season number which the episode is in.
            epNum {integer} -- The episode number in the season.

        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})
            id -- Optional input of show id when searching for episode names.

        Raises:
            InvalidInput: Raises if a non string is inputed for name.
            InvalidShowID: Raises if a show was not found.

        Returns:
            String -- Returns the name of the episode searched for, cleaned of all special characters.
        """
        if type(name) is not str or type(seasonNum) is not int or type(epNum) is not int or seasonNum < 0 or epNum < 1:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        if (id == None):
            id = self._getShowID(name, accuracy)
        else:
            return self._getEpisodeName(id, seasonNum, epNum, order)
        if id == -1:
            raise InvalidShowID
        return self._getEpisodeName(id, seasonNum, epNum, order)

    def getActors(self, name, accuracy=0.8):
        """Gets a dictionary of all actors for a given show as well as information on them, and returns it to the user.

        Arguments:
            name {String} -- The name of the show.

        Keyword Arguments:
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})

        Raises:
            InvalidInput: Raises if a non string is inputed for name.
            InvalidShowID: Raises if a show was not found.

        Returns:
            dict -- A dictionary of all actors for the show, as well as information about them.
        """
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name, accuracy)
        if id == -1:
            raise InvalidShowID("Show was not found, please try again")
        return self._getActors(id)

    def getImages(self, name, imageType="poster", accuracy=0.8):
        """Grabs the urls for the images of the show based on the type you have selected. Default grabs 'series' image urls,
        and returns them in a list.

        Arguments:
            name {String} -- The name of the show.

        Keyword Arguments:
            imageType {str} -- fanart, poster, season, seasonwide, series, all (default: {"series"})
            accuracy {float} -- If no show with title found, how accurate should a match to the alias be. (default: {0.8})

        Returns:
            list -- A list of the image urls for the given show.
        """
        if type(name) is not str:
            raise InvalidInput(
                "You have entered an invalid name. Please try again.")
        if not self.__authorized:
            self._authorize()
        id = self._getShowID(name, accuracy)
        return self._getImages(id, imageType)

    def _authorize(self):
        r = self.session.post(
            self.config['loginURL'], json=self.config['authPayload'], headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise InvalidCredentials
        token = r.get('token')
        self.headers['Authorization'] = f'Bearer {token}'
        self.__authorized = True

    def _getShowID(self, name, accuracy):
        params = {
            'name': name
        }
        r = self.session.get(
            self.config['searchEndpoint'], params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise ShowNotFound
        for show in r['data']:
            if SequenceMatcher(None, name.lower(), show['seriesName'].lower()).ratio() >= accuracy:
                return show['id']
            for alias in show['aliases']:
                if SequenceMatcher(None, name.lower(), alias.lower()).ratio() >= accuracy:
                    return show['id']
        return -1

    def _getEpisodeName(self, id, seasonNum, epNum, order):
        if 'DVD' in order:
            params = {
                'dvdSeason': seasonNum,
                'dvdEpisode': epNum
            }
        elif 'AIRED' in order:
            params = {
                'airedSeason': seasonNum,
                'airedEpisode': epNum
            }
        else:
            params = {
                'airedSeason': seasonNum,
                'airedEpisode': epNum
            }
        r = self.session.get(
            self.config['seriesEndpoint'] + f"/{id}/episodes/query", params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            # raise NoSuchEpisode("No episode could be found. Please check season or episode number and try again.")
            episodeName = self._fallbackGetEpisodeName(id, order, epNum)
            return episodeName
        return self._cleanName(r['data'][0]['episodeName'])

    def _fallbackGetEpisodeName(self, id, order, epNum):
        if id == -1:
            raise InvalidShowID("Show was not found, please try again")
        pages = self.session.get(
            self.config['seriesEndpoint'] + f"{id}/episodes", headers=self.headers).json()['links']['last']
        for x in range(1, pages+1):
            params = {
                "page": x
            }
            data = self.session.get(
                self.config['seriesEndpoint'] + f"{id}/episodes", params=params, headers=self.headers).json()['data']
            for episode in data:
                if 'DVD' in order and episode.dvdEpisodeNumber is epNum:
                    return self._cleanName(episode.episodeName)
                elif 'AIRED' in order and episode.airedEpisodeNumber is epNum:
                    return self._cleanName(episode.episodeName)
        raise NoSuchEpisode("No episode could be found. Please check season or episode number and try again.")

    def _getActors(self, showID):
        r = self.session.get(
            self.config['seriesEndpoint'] + f"{showID}/actors", headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise NoActorsFound("No actors found for specific show.")
        return r

    def _getImages(self, showID, imageType):
        images = []
        params = {
            'keyType': imageType
        }
        r = self.session.get(
            self.config['seriesEndpoint'] + f"{showID}/images/query?", params=params, headers=self.headers).json()
        error = r.get('Error')
        if error:
            raise NoImagesFound(
                "No images were found for the show of that type")
        for image in r['data']:
            images.append(self.config['imageURL'] + image['fileName'])
        return images

    def _cleanName(self, name):
        newName = name.replace('\\', "").replace("/", "").replace(":", "").replace("*", "").replace(
            "?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "").replace("\t", "")
        return newName

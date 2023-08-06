#!/usr/bin/env python3
from altvmasterlist import shared
from dataclasses import dataclass
from re import compile
import logging
import sys

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
"""You can find the masterlist api docs here: https://docs.altv.mp/articles/master_list_api.html"""


@dataclass
class Server:
    """This is the server object. All values will be fetched from the api
    in the __init__ function. You just need to provide the id like this: Server("example_id")

    Attributes:
        id: The server id.
        no_fetch: Define if you want to fetch the api data. This can be used when we already have data.
    """
    id: str
    active: bool = False
    maxPlayers: int = 0
    players: int = 0
    name: str = ""
    locked: bool = False
    host: str = ""
    port: int = 0
    gameMode: str = ""
    website: str = ""
    language: str = ""
    description: str = ""
    verified: bool = False
    promoted: bool = False
    useEarlyAuth: bool = False
    earlyAuthUrl: str = ""
    useCdn: bool = False
    cdnUrl: str = ""
    useVoiceChat: bool = False
    tags: list[str] = None
    bannerUrl: str = ""
    branch: str = ""
    build: str = ""
    version: float = 0.0
    lastUpdate: int = 0

    def __init__(self, server_id: str, no_fetch: bool = False) -> None:
        """Update the server data using the api."""
        self.id = server_id

        if not no_fetch:
            temp_data = shared.request(shared.MasterlistUrls.specific_server.value.format(self.id))
            if temp_data is None or temp_data == {} or not temp_data["active"]:
                # the api returned no data or the server is offline
                self.active = False
                self.players = 0
            else:
                self.active = temp_data["active"]
                self.maxPlayers = temp_data["info"]["maxPlayers"]
                self.players = temp_data["info"]["players"]
                self.name = temp_data["info"]["name"]
                self.locked = temp_data["info"]["locked"]
                self.host = temp_data["info"]["host"]
                self.port = temp_data["info"]["port"]
                self.gameMode = temp_data["info"]["gameMode"]
                self.website = temp_data["info"]["website"]
                self.language = temp_data["info"]["language"]
                self.description = temp_data["info"]["description"]
                self.verified = temp_data["info"]["verified"]
                self.promoted = temp_data["info"]["promoted"]
                self.useEarlyAuth = temp_data["info"]["useEarlyAuth"]
                self.earlyAuthUrl = temp_data["info"]["earlyAuthUrl"]
                self.useCdn = temp_data["info"]["useCdn"]
                self.cdnUrl = temp_data["info"]["cdnUrl"]
                self.useVoiceChat = temp_data["info"]["useVoiceChat"]
                self.tags = temp_data["info"]["tags"]
                self.bannerUrl = temp_data["info"]["bannerUrl"]
                self.branch = temp_data["info"]["branch"]
                self.build = temp_data["info"]["build"]
                self.version = temp_data["info"]["version"]
                self.lastUpdate = temp_data["info"]["lastUpdate"]

    def update(self) -> None:
        """Update the server data using the api."""
        self.__init__(self.id)

    def get_max(self, time: str = "1d") -> dict | None:
        """Maximum - Returns maximum data about the specified server (TIME = 1d, 7d, 31d)

        Args:
            time (str): The timerange of the data. Can be 1d, 7d, 31d.

        Returns:
            None: When an error occurs
            dict: The maximum player data
        """
        return shared.request(shared.MasterlistUrls.specific_server_maximum.value.format(self.id, time))

    def get_avg(self, time: str = "1d", return_result: bool = False) -> dict | int | None:
        """Averages - Returns averages data about the specified server (TIME = 1d, 7d, 31d)

        Args:
            time (str): The timerange of the data. Can be 1d, 7d, 31d.
            return_result (bool): Define if you want the overall average.

        Returns:
            None: When an error occurs
            dict: The maximum player data
            int: Overall average of defined timerange
        """
        average_data = shared.request(shared.MasterlistUrls.specific_server_average.value.format(self.id, time))
        if not average_data:
            return None

        if return_result:
            players_all = 0
            for entry in average_data:
                players_all = players_all + entry["c"]
            result = players_all / len(average_data)
            return round(result)
        else:
            return average_data

    @property
    def connect_json(self) -> dict | None:
        """Get the connect.json of the server."""
        return shared.fetch_connect_json(self.useCdn, self.locked, self.active, self.host, self.port, self.cdnUrl)

    @property
    def permissions(self) -> shared.Permissions | None:
        """Get the permissions of the server."""
        return shared.get_permissions(self.connect_json)

    def get_dtc_url(self, password=None) -> str | None:
        """Get the dtc url of the server."""
        return shared.get_dtc_url(self.useCdn, self.cdnUrl, self.host, self.port, self.locked, password)

    def get_resource_size(self, resource: str, decimal: int = 2) -> float | None:
        """Get the size of a server resource."""
        return shared.get_resource_size(self.useCdn, self.cdnUrl, resource, self.host, self.port, decimal)


def get_server_stats() -> dict | None:
    """Statistics - Player Count across all servers & The amount of servers online

    Returns:
        None: When an error occurs
        dict: The stats
    """
    data = shared.request(shared.MasterlistUrls.all_server_stats.value)
    if data is None:
        return None
    else:
        return data


def get_servers() -> list[Server] | None:
    """Generates a list of all servers that are currently online.
    Note that the server objects returned are not complete!

    Returns:
        None: When an error occurs
        list: List object that contains all servers.
    """
    return_servers = []
    servers = shared.request(shared.MasterlistUrls.all_servers.value)
    if servers is None or servers == "{}":
        return None
    else:
        for server in servers:
            tmp_server = Server(server["id"], no_fetch=True)
            tmp_server.active = True
            tmp_server.maxPlayers = server["maxPlayers"]
            tmp_server.players = server["players"]
            tmp_server.name = server["name"]
            tmp_server.locked = server["locked"]
            tmp_server.host = server["host"]
            tmp_server.port = server["port"]
            tmp_server.gameMode = server["gameMode"]
            tmp_server.website = server["website"]
            tmp_server.language = server["language"]
            tmp_server.description = server["description"]
            tmp_server.verified = server["verified"]
            tmp_server.promoted = server["promoted"]
            tmp_server.useEarlyAuth = server["useEarlyAuth"]
            tmp_server.earlyAuthUrl = server["earlyAuthUrl"]
            tmp_server.useCdn = server["useCdn"]
            tmp_server.cdnUrl = server["cdnUrl"]
            tmp_server.useVoiceChat = server["useVoiceChat"]
            tmp_server.tags = server["tags"]
            tmp_server.bannerUrl = server["bannerUrl"]
            tmp_server.branch = server["branch"]
            tmp_server.build = server["build"]
            tmp_server.version = server["version"]
            tmp_server.lastUpdate = server["lastUpdate"]
            return_servers.append(tmp_server)

        return return_servers


def validate_id(server_id: any) -> bool:
    """Validate a server id

    Args:
        server_id (any): The id you want to check.

    Returns:
        bool: True = valid, False = invalid
    """
    if not isinstance(server_id, str):
        return False
    regex = compile(r"^[\da-zA-Z]{32}$")
    result = regex.match(server_id)
    if result is not None:
        return True
    else:
        return False


def get_launcher_skins() -> dict | None:
    """Get a list of all available launcher skins.

    Returns:
        json: A json array of all launcher skins.

    The elements have the following keys: serverId, xxHash64 and fileName.
    """
    skins = shared.request(shared.MasterlistUrls.launcher_skins.value)

    if skins is None or skins == "{}":
        return None
    else:
        return skins["indexEntries"]


def get_launcher_skin(filename: str) -> dict | None:
    """Get a specific launcher skin by filename

    Args:
        filename (str): filename of the launcher skin

    Returns:
        json: Object

    The json object has the following keys:
        - name: the name of the server
        - id: the server id
        - rss: the custom rss feed of the server
        - primaryColor: the custom color of the server
        - servers (array): list of servers
            - name: server name
            - url: direct connect url
            - id: server id
            - imageSplash64: base64 splash image
            - imageLogo64: base64 Logo
            - imageBackground64: base64 background image

    """
    if not filename or filename == "":
        return None

    skin = shared.request(shared.MasterlistUrls.launcher_skins_file.value.format(filename))

    if skin is None or skin == {}:
        return None
    else:
        return skin


if __name__ == "__main__":
    print("This is a Module!")
    sys.exit()

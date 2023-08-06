#!/usr/bin/env python3
from altvmasterlist import shared
from dataclasses import dataclass
from re import compile
import logging
import sys

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
"""You can find the altstats api docs here: https://docs.altv.mp/articles/master_list_api.html#information-1"""


@dataclass
class Server:
    """This is the server object. All values will be fetched from the api
        in the __init__ function. You just need to provide the id like this: Server("example_id")

    Attributes:
        Id: The server id.
        no_fetch: Define if you want to fetch the api data. This can be used when we already have data.
    """
    Id: int
    FoundAt: str = ""
    LastActivity: bool = False
    Visible: bool = False
    ServerId: str = ""
    Players: int = 0
    Name: str = ""
    Locked: bool = False
    Ip: str = ""
    Port: int = 0
    MaxPlayers: int = 0
    Ping: int = 0
    Website: str = ""
    Language: str = ""
    Description: str = ""
    LastUpdate: int = 0
    IsOfficial: bool = False
    PlayerRecord: int = 0
    PlayerRecordDate: str = ""
    LastFetchOnline: bool = False
    LanguageShort: str = ""
    GameMode: str = ""
    Branch: str = ""
    Build: int = 0
    CdnUrl: str = ""
    EarlyAuthUrl: str = ""
    Verified: bool = False
    UseCdn: bool = False
    UseEarlyAuth: bool = False
    BannerUrl: str = ""
    Promoted: bool = False
    Tags: list[str] = None
    UseVoiceChat: bool = False
    Level: int = 0
    Version: float = 0.0

    def __init__(self, server_id: int, no_fetch: bool = False) -> None:
        """Update the server data using the api."""
        self.Id = server_id

        if not no_fetch:
            temp_data = shared.request(shared.AltstatsUrls.specific_server.value.format(self.Id))
            if temp_data is None or temp_data == {} or not temp_data["LastUpdate"]:
                # the api returned no data or the server is offline
                self.LastActivity = False
                self.Players = 0
            else:
                self.FoundAt = temp_data["FoundAt"]
                self.LastActivity = temp_data["LastActivity"]
                self.Visible = temp_data["Visible"]
                self.ServerId = temp_data["ServerId"]
                self.Players = temp_data["Players"]
                self.Name = temp_data["Name"]
                self.Locked = temp_data["Locked"]
                self.Ip = temp_data["Ip"]
                self.Port = temp_data["Port"]
                self.MaxPlayers = temp_data["MaxPlayers"]
                self.Ping = temp_data["Ping"]
                self.Website = temp_data["Website"]
                self.Language = temp_data["Language"]
                self.Description = temp_data["Description"]
                self.LastUpdate = temp_data["LastUpdate"]
                self.IsOfficial = temp_data["IsOfficial"]
                self.PlayerRecord = temp_data["PlayerRecord"]
                self.PlayerRecordDate = temp_data["PlayerRecordDate"]
                self.LastFetchOnline = temp_data["LastFetchOnline"]
                self.LanguageShort = temp_data["LanguageShort"]
                self.GameMode = temp_data["GameMode"]
                self.Branch = temp_data["Branch"]
                self.Build = temp_data["Build"]
                self.CdnUrl = temp_data["CdnUrl"]
                self.EarlyAuthUrl = temp_data["EarlyAuthUrl"]
                self.Verified = temp_data["Verified"]
                self.UseCdn = temp_data["UseCdn"]
                self.UseEarlyAuth = temp_data["UseEarlyAuth"]
                self.BannerUrl = temp_data["BannerUrl"]
                self.Promoted = temp_data["Promoted"]
                self.Tags = temp_data["Tags"]
                self.UseVoiceChat = temp_data["UseVoiceChat"]
                self.Level = temp_data["Level"]
                self.Version = temp_data["Version"]

    def update(self) -> None:
        """Update the server data using the api."""
        self.__init__(self.Id)

    @property
    def connect_json(self) -> dict | None:
        """Get the connect.json of the server."""
        return shared.fetch_connect_json(self.UseCdn, self.Locked, self.LastFetchOnline,
                                         self.Ip, self.Port, self.CdnUrl)

    @property
    def permissions(self) -> shared.Permissions | None:
        """Get the permissions of the server."""
        return shared.get_permissions(self.connect_json)

    def get_dtc_url(self, password: str = None) -> str | None:
        """Get the dtc url of the server."""
        return shared.get_dtc_url(self.UseCdn, self.CdnUrl, self.Ip, self.Port, self.Locked, password)

    def get_resource_size(self, resource: str, decimal: int = 2) -> float | None:
        """Get the size of a server resource."""
        return shared.get_resource_size(self.UseCdn, self.CdnUrl, resource, self.Ip, self.Port, decimal)


def get_server_stats() -> dict | None:
    """Statistics - Player Count across all servers & The amount of servers online

    Returns:
        None: When an error occurs
        dict: The stats
    """
    data = shared.request(shared.AltstatsUrls.all_server_stats.value)
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
    servers = shared.request(shared.AltstatsUrls.all_servers.value)
    if servers is None or servers == "{}":
        return None
    else:
        for server in servers:
            tmp_server = Server(server["id"], True)
            tmp_server.Name = server["name"]
            tmp_server.Locked = bool(server["locked"])
            tmp_server.Players = server["playerCount"]
            tmp_server.MaxPlayers = server["slots"]
            tmp_server.gameMode = server["gameMode"]
            tmp_server.language = server["language"]
            tmp_server.IsOfficial = bool(server["official"])
            tmp_server.Verified = bool(server["verified"])
            tmp_server.Promoted = bool(server["promoted"])
            tmp_server.Tags = server["tags"]
            return_servers.append(tmp_server)

        return return_servers


def validate_id(server_id: any) -> bool:
    """Validate a server id

    Args:
        server_id (any): The id you want to check.

    Returns:
        bool: True = valid, False = invalid
    """
    if not isinstance(server_id, str) and not isinstance(server_id, int):
        return False
    server_id = str(server_id)
    regex = compile(r"^\d+$")
    result = regex.match(server_id)
    if result is not None:
        return True
    else:
        return False


if __name__ == "__main__":
    print("This is a Module!")
    sys.exit()

"""
Service for managing Trello boards in MCP server.
"""

from typing import List

from server.models import TrelloBoard, TrelloLabel, TrelloMember
from server.utils.trello_api import TrelloClient


class BoardService:
    """
    Service class for managing Trello boards
    """

    def __init__(self, client: TrelloClient):
        self.client = client

    async def get_board(self, board_id: str) -> TrelloBoard:
        """Retrieves a specific board by its ID.

        Args:
            board_id (str): The ID of the board to retrieve.

        Returns:
            TrelloBoard: The board object containing board details.
        """
        response = await self.client.GET(f"/boards/{board_id}")
        return TrelloBoard(**response)

    async def get_boards(self, member_id: str = "me", filter: str = "all") -> List[TrelloBoard]:
        """Retrieves all boards for a given member.

        Args:
            member_id (str): The ID of the member whose boards to retrieve. Defaults to "me" for the authenticated user.
            filter (str): Filter to apply. Can be "all", "open", "closed", "members", "organization", "public", "private". Defaults to "all".

        Returns:
            List[TrelloBoard]: A list of board objects.
        """
        params = {"filter": filter}
        response = await self.client.GET(f"/members/{member_id}/boards", params=params)
        return [TrelloBoard(**board) for board in response]

    async def get_board_labels(self, board_id: str) -> List[TrelloLabel]:
        """Retrieves all labels for a specific board.

        Args:
            board_id (str): The ID of the board whose labels to retrieve.

        Returns:
            List[TrelloLabel]: A list of label objects for the board.
        """
        response = await self.client.GET(f"/boards/{board_id}/labels")
        return [TrelloLabel(**label) for label in response]

    async def get_board_members(self, board_id: str) -> List[TrelloMember]:
        """Retrieves all members for a specific board.

        Args:
            board_id (str): The ID of the board whose members to retrieve.

        Returns:
            List[TrelloMember]: A list of member objects for the board.
        """
        response = await self.client.GET(f"/boards/{board_id}/members")
        return [TrelloMember(**member) for member in response]

    async def create_board(
        self,
        name: str,
        desc: str | None = None,
        idOrganization: str | None = None,
        idBoardSource: str | None = None,
        keepFromSource: str | None = None,
        powerUps: str | None = None,
        defaultLabels: bool = True,
        defaultLists: bool = True,
        prefs_permissionLevel: str | None = None,
        prefs_voting: str | None = None,
        prefs_comments: str | None = None,
        prefs_invitations: str | None = None,
        prefs_selfJoin: bool | None = None,
        prefs_cardCovers: bool | None = None,
        prefs_background: str | None = None,
        prefs_cardAging: str | None = None,
    ) -> TrelloBoard:
        """Creates a new board.

        Args:
            name (str): The name of the board to create.
            desc (str, optional): The description of the board.
            idOrganization (str, optional): The ID of the organization to add the board to.
            idBoardSource (str, optional): The ID of a board to copy from.
            keepFromSource (str, optional): What to copy from the source board. Can be "all", "cards", "none".
            powerUps (str, optional): Power-ups to enable on the board.
            defaultLabels (bool, optional): Whether to create default labels. Defaults to True.
            defaultLists (bool, optional): Whether to create default lists. Defaults to True.
            prefs_permissionLevel (str, optional): Permission level. Can be "org", "private", "public".
            prefs_voting (str, optional): Voting preferences. Can be "disabled", "members", "observers", "org", "public".
            prefs_comments (str, optional): Comment preferences. Can be "disabled", "members", "observers", "org", "public".
            prefs_invitations (str, optional): Invitation preferences. Can be "admins", "members".
            prefs_selfJoin (bool, optional): Whether members can join themselves.
            prefs_cardCovers (bool, optional): Whether card covers are enabled.
            prefs_background (str, optional): Background color or image.
            prefs_cardAging (str, optional): Card aging style. Can be "regular", "pirate".

        Returns:
            TrelloBoard: The newly created board object.
        """
        # Build JSON body data
        json_data = {"name": name}
        if desc is not None:
            json_data["desc"] = desc
        if idOrganization is not None:
            json_data["idOrganization"] = idOrganization
        if idBoardSource is not None:
            json_data["idBoardSource"] = idBoardSource
        if keepFromSource is not None:
            json_data["keepFromSource"] = keepFromSource
        if powerUps is not None:
            json_data["powerUps"] = powerUps
        json_data["defaultLabels"] = str(defaultLabels).lower()
        json_data["defaultLists"] = str(defaultLists).lower()
        
        # Preferences need to be passed as query parameters (with "/" in the name)
        # We'll need to modify the POST method to accept both json_data and params
        # For now, let's include them in the data dict - Trello API accepts them in the body
        if prefs_permissionLevel is not None:
            json_data["prefs/permissionLevel"] = prefs_permissionLevel
        if prefs_voting is not None:
            json_data["prefs/voting"] = prefs_voting
        if prefs_comments is not None:
            json_data["prefs/comments"] = prefs_comments
        if prefs_invitations is not None:
            json_data["prefs/invitations"] = prefs_invitations
        if prefs_selfJoin is not None:
            json_data["prefs/selfJoin"] = str(prefs_selfJoin).lower()
        if prefs_cardCovers is not None:
            json_data["prefs/cardCovers"] = str(prefs_cardCovers).lower()
        if prefs_background is not None:
            json_data["prefs/background"] = prefs_background
        if prefs_cardAging is not None:
            json_data["prefs/cardAging"] = prefs_cardAging

        response = await self.client.POST("/boards", data=json_data)
        return TrelloBoard(**response)

    async def create_board_label(self, board_id: str, **kwargs) -> TrelloLabel:
        """Create label for a specific board.

        Args:
            board_id (str): The ID of the board whose to add label.

        Returns:
            List[TrelloLabel]: A list of label objects for the board.
        """
        response = await self.client.POST(f"/boards/{board_id}/labels", data=kwargs)
        return TrelloLabel(**response)

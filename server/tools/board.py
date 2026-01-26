"""
This module contains tools for managing Trello boards.
"""

import logging
from typing import List, Optional

from mcp.server.fastmcp import Context
from fastmcp.tools.tool import ToolResult

from server.models import TrelloBoard, TrelloLabel, TrelloMember, TrelloCard, TrelloList
from server.dtos.create_label import CreateLabelPayload
from server.services.board import BoardService
from server.services.list import ListService
from server.services.card import CardService
from server.trello import client

logger = logging.getLogger(__name__)

service = BoardService(client)
list_service = ListService(client)
card_service = CardService(client)


async def get_board(ctx: Context, board_id: str) -> TrelloBoard:
    """Retrieves a specific board by its ID.

    Args:
        board_id (str): The ID of the board to retrieve.

    Returns:
        TrelloBoard: The board object containing board details.
    """
    try:
        logger.info(f"Getting board with ID: {board_id}")
        result = await service.get_board(board_id)
        logger.info(f"Successfully retrieved board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_boards(ctx: Context) -> str:
    """Retrieves all boards for the authenticated user and returns them as formatted text.

    Returns:
        str: A formatted string listing all boards with their details.
    """
    try:
        logger.info("=" * 50)
        logger.info("get_boards called - START")
        result = await service.get_boards()
        logger.info(f"Successfully retrieved {len(result)} boards from Trello API")
        
        if not result:
            logger.info("No boards found, returning 'No boards found.'")
            return "No boards found."
        
        # Log each board retrieved
        for i, board in enumerate(result, 1):
            logger.info(f"Board {i}: {board.name} (ID: {board.id}, Closed: {board.closed})")
        
        # Format boards as a readable string
        boards_text = f"Found {len(result)} board(s):\n\n"
        for i, board in enumerate(result, 1):
            boards_text += f"{i}. {board.name}\n"
            boards_text += f"   ID: {board.id}\n"
            boards_text += f"   URL: {board.url}\n"
            boards_text += f"   Status: {'Closed' if board.closed else 'Open'}\n"
            if board.desc:
                boards_text += f"   Description: {board.desc[:100]}{'...' if len(board.desc) > 100 else ''}\n"
            if board.idOrganization:
                boards_text += f"   Organization ID: {board.idOrganization}\n"
            boards_text += "\n"
        
        logger.info(f"Returning formatted text with length: {len(boards_text)} characters")
        logger.info(f"First 200 chars of response: {boards_text[:200]}")
        logger.info("get_boards called - END")
        logger.info("=" * 50)
        
        return boards_text
    except Exception as e:
        error_msg = f"Failed to get boards: {str(e)}"
        logger.error(error_msg)
        logger.exception("Full exception traceback:")
        await ctx.error(error_msg)
        raise


async def list_all_boards(ctx: Context) -> str:
    """Lists all boards for the authenticated user in a formatted text format.

    This is an alternative to get_boards that returns boards as formatted text
    to avoid serialization issues with lists.

    Returns:
        str: A formatted string listing all boards with their details.
    """
    try:
        logger.info("Listing all boards")
        result = await service.get_boards()
        logger.info(f"Successfully retrieved {len(result)} boards")
        
        if not result:
            return "No boards found."
        
        # Format boards as a readable string
        boards_text = f"Found {len(result)} board(s):\n\n"
        for i, board in enumerate(result, 1):
            boards_text += f"{i}. {board.name}\n"
            boards_text += f"   ID: {board.id}\n"
            boards_text += f"   URL: {board.url}\n"
            boards_text += f"   Status: {'Closed' if board.closed else 'Open'}\n"
            if board.desc:
                boards_text += f"   Description: {board.desc[:100]}{'...' if len(board.desc) > 100 else ''}\n"
            boards_text += "\n"
        
        return boards_text
    except Exception as e:
        error_msg = f"Failed to list boards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_board_labels(ctx: Context, board_id: str) -> List[TrelloLabel]:
    """Retrieves all labels for a specific board.

    Args:
        board_id (str): The ID of the board whose labels to retrieve.

    Returns:
        List[TrelloLabel]: A list of label objects for the board.
    """
    try:
        logger.info(f"Getting labels for board: {board_id}")
        result = await service.get_board_labels(board_id)
        logger.info(f"Successfully retrieved {len(result)} labels for board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board labels: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_board_members(ctx: Context, board_id: str) -> List[TrelloMember]:
    """Retrieves all members for a specific board.

    Args:
        board_id (str): The ID of the board whose members to retrieve.

    Returns:
        List[TrelloMember]: A list of member objects for the board.
    """
    try:
        logger.info(f"Getting members for board: {board_id}")
        result = await service.get_board_members(board_id)
        logger.info(f"Successfully retrieved {len(result)} members for board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board members: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_board(
    ctx: Context,
    name: str,
    desc: str | None = None,
    idOrganization: str | None = None,
    defaultLists: bool = True,
    defaultLabels: bool = True,
    prefs_permissionLevel: str | None = None,
) -> TrelloBoard:
    """Creates a new board.

    Args:
        name (str): The name of the board to create.
        desc (str, optional): The description of the board.
        idOrganization (str, optional): The ID of the organization to add the board to.
        defaultLists (bool, optional): Whether to create default lists (To Do, Doing, Done). Defaults to True.
        defaultLabels (bool, optional): Whether to create default labels. Defaults to True.
        prefs_permissionLevel (str, optional): Permission level. Can be "org", "private", "public".

    Returns:
        TrelloBoard: The newly created board object.
    """
    try:
        logger.info(f"Creating board with name: {name}")
        result = await service.create_board(
            name=name,
            desc=desc,
            idOrganization=idOrganization,
            defaultLists=defaultLists,
            defaultLabels=defaultLabels,
            prefs_permissionLevel=prefs_permissionLevel,
        )
        logger.info(f"Successfully created board: {result.id}")
        return result
    except Exception as e:
        error_msg = f"Failed to create board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_board_with_tasks(
    ctx: Context,
    board_name: str,
    board_desc: str | None = None,
    list_names: List[str] | None = None,
    tasks: list | None = None,
    idOrganization: str | None = None,
    prefs_permissionLevel: str | None = None,
) -> dict:
    """Creates a new board with custom lists and tasks.

    This is a high-level tool that creates a complete board setup:
    1. Creates a new board
    2. Creates custom lists (or uses default lists)
    3. Creates tasks in the specified lists

    Args:
        board_name (str): The name of the board to create.
        board_desc (str, optional): The description of the board.
        list_names (List[str], optional): List of list names to create. If not provided, defaults to ["To Do", "Doing", "Done"].
        tasks (list, optional): List of tasks to create. Each task should be a dictionary with:
            - name (str): Task name
            - desc (str, optional): Task description
            - list_name (str): Name of the list to create the task in
            - idLabels (str, optional): Comma-separated label IDs
            - idMembers (str, optional): Comma-separated member IDs
            - due (str, optional): Due date in ISO 8601 format
        idOrganization (str, optional): The ID of the organization to add the board to.
        prefs_permissionLevel (str, optional): Permission level. Can be "org", "private", "public".

    Returns:
        dict: A dictionary containing:
            - board: The created board object
            - lists: List of created list objects
            - cards: List of created card objects
    """
    try:
        # Step 1: Create the board
        logger.info(f"Creating board '{board_name}' with tasks")
        board = await service.create_board(
            name=board_name,
            desc=board_desc,
            idOrganization=idOrganization,
            defaultLists=False,  # We'll create custom lists
            defaultLabels=True,
            prefs_permissionLevel=prefs_permissionLevel,
        )
        logger.info(f"Successfully created board: {board.id}")

        # Step 2: Create lists
        if list_names is None:
            list_names = ["To Do", "Doing", "Done"]
        
        created_lists = []
        list_name_to_id = {}
        
        for i, list_name in enumerate(list_names):
            pos = "top" if i == 0 else "bottom"
            trello_list = await list_service.create_list(board.id, list_name, pos=pos)
            created_lists.append(trello_list)
            list_name_to_id[list_name] = trello_list.id
            logger.info(f"Created list '{list_name}' with ID: {trello_list.id}")

        # Step 3: Create tasks if provided
        created_cards = []
        if tasks:
            for task in tasks:
                task_name = task.get("name")
                if not task_name:
                    logger.warning("Skipping task without name")
                    continue
                
                list_name = task.get("list_name", list_names[0])  # Default to first list
                list_id = list_name_to_id.get(list_name)
                
                if not list_id:
                    logger.warning(f"List '{list_name}' not found, using first list")
                    list_id = created_lists[0].id
                
                # Build card payload
                card_payload = {
                    "idList": list_id,
                    "name": task_name,
                }
                
                if "desc" in task:
                    card_payload["desc"] = task["desc"]
                if "idLabels" in task:
                    card_payload["idLabels"] = task["idLabels"]
                if "idMembers" in task:
                    card_payload["idMembers"] = task["idMembers"]
                if "due" in task:
                    card_payload["due"] = task["due"]
                if "start" in task:
                    card_payload["start"] = task["start"]
                
                card = await card_service.create_card(**card_payload)
                created_cards.append(card)
                logger.info(f"Created card '{task_name}' in list '{list_name}'")

        result = {
            "board": board.model_dump(),
            "lists": [lst.model_dump() for lst in created_lists],
            "cards": [card.model_dump() for card in created_cards],
        }
        
        logger.info(f"Successfully created board '{board_name}' with {len(created_lists)} lists and {len(created_cards)} tasks")
        return result
        
    except Exception as e:
        error_msg = f"Failed to create board with tasks: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_tasks_in_board(
    ctx: Context,
    board_id: str,
    tasks: list,
    create_missing_lists: bool = True,
) -> dict:
    """Creates tasks in an existing board.

    This tool creates multiple tasks in an existing board. It can:
    - Create tasks in existing lists (by list name or ID)
    - Optionally create new lists if they don't exist

    Args:
        board_id (str): The ID of the existing board.
        tasks (list): List of tasks to create. Each task should be a dictionary with:
            - name (str): Task name (required)
            - desc (str, optional): Task description
            - list_name (str, optional): Name of the list to create the task in
            - list_id (str, optional): ID of the list to create the task in (takes precedence over list_name)
            - idLabels (str, optional): Comma-separated label IDs
            - idMembers (str, optional): Comma-separated member IDs
            - due (str, optional): Due date in ISO 8601 format
            - start (str, optional): Start date in ISO 8601 format
        create_missing_lists (bool, optional): If True, creates lists that don't exist. Defaults to True.

    Returns:
        dict: A dictionary containing:
            - board_id: The board ID
            - created_lists: List of newly created list objects (if any)
            - created_cards: List of created card objects
            - errors: List of any errors encountered
    """
    try:
        logger.info(f"Creating tasks in board: {board_id}")
        
        # Get existing board to verify it exists
        board = await service.get_board(board_id)
        logger.info(f"Found board: {board.name}")
        
        # Get existing lists in the board
        existing_lists = await list_service.get_lists(board_id)
        list_name_to_id = {lst.name: lst.id for lst in existing_lists}
        list_id_to_obj = {lst.id: lst for lst in existing_lists}
        
        created_lists = []
        created_cards = []
        errors = []
        
        # Process each task
        for task in tasks:
            try:
                task_name = task.get("name")
                if not task_name:
                    errors.append("Task missing required 'name' field")
                    continue
                
                # Determine which list to use
                list_id = None
                list_name = None
                
                # Priority: list_id > list_name
                if "list_id" in task and task["list_id"]:
                    list_id = task["list_id"]
                    if list_id in list_id_to_obj:
                        list_name = list_id_to_obj[list_id].name
                elif "list_name" in task and task["list_name"]:
                    list_name = task["list_name"]
                    list_id = list_name_to_id.get(list_name)
                    
                    # Create list if it doesn't exist and create_missing_lists is True
                    if not list_id and create_missing_lists:
                        logger.info(f"Creating new list '{list_name}' in board {board_id}")
                        new_list = await list_service.create_list(board_id, list_name, pos="bottom")
                        created_lists.append(new_list)
                        list_id = new_list.id
                        list_name_to_id[list_name] = list_id
                        list_id_to_obj[list_id] = new_list
                        logger.info(f"Created list '{list_name}' with ID: {list_id}")
                
                # If still no list_id, use first available list or error
                if not list_id:
                    if existing_lists:
                        list_id = existing_lists[0].id
                        list_name = existing_lists[0].name
                        logger.warning(f"No list specified for task '{task_name}', using first list: {list_name}")
                    else:
                        errors.append(f"Task '{task_name}': No list specified and no lists available")
                        continue
                
                # Build card payload
                card_payload = {
                    "idList": list_id,
                    "name": task_name,
                }
                
                if "desc" in task:
                    card_payload["desc"] = task["desc"]
                if "idLabels" in task:
                    card_payload["idLabels"] = task["idLabels"]
                if "idMembers" in task:
                    card_payload["idMembers"] = task["idMembers"]
                if "due" in task:
                    card_payload["due"] = task["due"]
                if "start" in task:
                    card_payload["start"] = task["start"]
                
                card = await card_service.create_card(**card_payload)
                created_cards.append(card)
                logger.info(f"Created card '{task_name}' in list '{list_name or list_id}'")
                
            except Exception as e:
                error_msg = f"Error creating task '{task.get('name', 'unknown')}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue
        
        result = {
            "board_id": board_id,
            "board_name": board.name,
            "created_lists": [lst.model_dump() for lst in created_lists],
            "created_cards": [card.model_dump() for card in created_cards],
            "errors": errors,
        }
        
        logger.info(f"Successfully created {len(created_cards)} tasks in board '{board.name}'")
        if created_lists:
            logger.info(f"Created {len(created_lists)} new lists")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors")
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to create tasks in board: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_board_label(ctx: Context, board_id: str, payload: CreateLabelPayload) -> TrelloLabel:
    """Create label for a specific board.

    Args:
        board_id (str): The ID of the board whose to add label to.
        name (str): The name of the label.
        color (str): The color of the label.

    Returns:
        TrelloLabel: A label object for the board.
    """
    try:
        logger.info(f"Creating label {payload.name} label for board: {board_id}")
        result = await service.create_board_label(board_id, **payload.model_dump(exclude_unset=True))
        logger.info(f"Successfully created label {payload.name} labels for board: {board_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get board labels: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


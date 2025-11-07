"""
This module contains tools for managing Trello cards.
"""

import json
import logging
from typing import List, Union

from mcp.server.fastmcp import Context

from server.models import TrelloCard
from server.services.card import CardService
from server.trello import client
from server.dtos.update_card import UpdateCardPayload
from server.dtos.create_card import CreateCardPayload

logger = logging.getLogger(__name__)

service = CardService(client)


async def get_card(ctx: Context, card_id: str) -> TrelloCard:
    """Retrieves a specific card by its ID.

    Args:
        card_id (str): The ID of the card to retrieve.

    Returns:
        TrelloCard: The card object containing card details.
    """
    try:
        logger.info(f"Getting card with ID: {card_id}")
        result = await service.get_card(card_id)
        logger.info(f"Successfully retrieved card: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_cards(ctx: Context, list_id: str) -> List[TrelloCard]:
    """Retrieves all cards in a given list.

    Args:
        list_id (str): The ID of the list whose cards to retrieve.

    Returns:
        List[TrelloCard]: A list of card objects.
    """
    try:
        logger.info(f"Getting cards for list: {list_id}")
        result = await service.get_cards(list_id)
        logger.info(f"Successfully retrieved {len(result)} cards for list: {list_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to get cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_card(
    ctx: Context,
    idList: str,
    name: str,
    desc: str | None = None,
    idLabels: str | None = None,
    idMembers: str | None = None,
    pos: str | None = None,
    due: str | None = None,
    start: str | None = None,
    dueComplete: bool | None = None,
    closed: bool | None = None,
    subscribed: bool | None = None,
    idBoard: str | None = None,
) -> TrelloCard:
    """Creates a new card in a given list.

    Args:
        idList (str): The ID of the list to create the card in.
        name (str): The name of the new card.
        desc (str, optional): The description of the new card.
        idLabels (str, optional): Comma-separated list of label IDs.
        idMembers (str, optional): Comma-separated list of member IDs.
        pos (str | int, optional): The position of the card.
        due (str, optional): The due date in ISO 8601 format.
        start (str, optional): The start date in ISO 8601 format.
        dueComplete (bool, optional): Whether the card is due complete.
        closed (bool, optional): Whether the card is closed.
        subscribed (bool, optional): Whether the card is subscribed.
        idBoard (str, optional): The ID of the board.

    Returns:
        TrelloCard: The newly created card object.
    """
    try:
        # Build payload dict with only provided values
        payload_dict = {
            "idList": idList,
            "name": name,
        }
        if desc is not None:
            payload_dict["desc"] = desc
        if idLabels is not None:
            payload_dict["idLabels"] = idLabels
        if idMembers is not None:
            payload_dict["idMembers"] = idMembers
        if pos is not None:
            payload_dict["pos"] = pos
        if due is not None:
            payload_dict["due"] = due
        if start is not None:
            payload_dict["start"] = start
        if dueComplete is not None:
            payload_dict["dueComplete"] = dueComplete
        if closed is not None:
            payload_dict["closed"] = closed
        if subscribed is not None:
            payload_dict["subscribed"] = subscribed
        if idBoard is not None:
            payload_dict["idBoard"] = idBoard
        
        logger.info(f"Creating card in list {idList} with name: {name}")
        result = await service.create_card(**payload_dict)
        logger.info(f"Successfully created card in list: {idList}")
        return result
    except Exception as e:
        error_msg = f"Failed to create card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def update_card(
    ctx: Context,
    card_id: str,
    name: str | None = None,
    desc: str | None = None,
    idLabels: str | None = None,
    idMembers: str | None = None,
    idList: str | None = None,
    pos: str | None = None,
    due: str | None = None,
    start: str | None = None,
    dueComplete: bool | None = None,
    closed: bool | None = None,
    subscribed: bool | None = None,
    idBoard: str | None = None,
) -> TrelloCard:
    """Updates a card's attributes.

    Args:
        card_id (str): The ID of the card to update.
        name (str, optional): The name of the card.
        desc (str, optional): The description of the card.
        idLabels (str, optional): Comma-separated list of label IDs. Can also be a single ID.
        idMembers (str, optional): Comma-separated list of member IDs. Can also be a single ID.
        idList (str, optional): The ID of the list the card is in.
        pos (str | int, optional): The position of the card.
        due (str, optional): The due date in ISO 8601 format.
        start (str, optional): The start date in ISO 8601 format.
        dueComplete (bool, optional): Whether the card is due complete.
        closed (bool, optional): Whether the card is closed.
        subscribed (bool, optional): Whether the card is subscribed.
        idBoard (str, optional): The ID of the board.

    Returns:
        TrelloCard: The updated card object.
    """
    try:
        # Build payload dict with only provided values
        payload_dict = {}
        if name is not None:
            payload_dict["name"] = name
        if desc is not None:
            payload_dict["desc"] = desc
        if idLabels is not None:
            # Log the received value for debugging
            logger.info(f"Received idLabels parameter: '{idLabels}' (length: {len(idLabels)})")
            # Ensure it's treated as a string and not truncated
            idLabels_str = str(idLabels).strip()
            if idLabels_str:
                payload_dict["idLabels"] = idLabels_str
                logger.info(f"Setting idLabels in payload: '{payload_dict['idLabels']}'")
        if idMembers is not None:
            # Log the received value for debugging
            logger.info(f"Received idMembers parameter: '{idMembers}' (length: {len(idMembers)})")
            # Ensure it's treated as a string and not truncated
            idMembers_str = str(idMembers).strip()
            if idMembers_str:
                payload_dict["idMembers"] = idMembers_str
                logger.info(f"Setting idMembers in payload: '{payload_dict['idMembers']}'")
        if idList is not None:
            payload_dict["idList"] = idList
        if pos is not None:
            payload_dict["pos"] = pos
        if due is not None:
            payload_dict["due"] = due
        if start is not None:
            payload_dict["start"] = start
        if dueComplete is not None:
            payload_dict["dueComplete"] = dueComplete
        if closed is not None:
            payload_dict["closed"] = closed
        if subscribed is not None:
            payload_dict["subscribed"] = subscribed
        if idBoard is not None:
            payload_dict["idBoard"] = idBoard
        
        logger.info(f"Updating card: {card_id} with payload: {payload_dict}")
        result = await service.update_card(card_id, **payload_dict)
        logger.info(f"Successfully updated card: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to update card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def add_label_to_card(ctx: Context, card_id: str, label_id: str) -> dict:
    """Adds a label to a card.

    Args:
        card_id (str): The ID of the card.
        label_id (str): The ID of the label to add.

    Returns:
        dict: The response from the add operation.
    """
    try:
        logger.info(f"Adding label {label_id} to card {card_id}")
        result = await service.add_label_to_card(card_id, label_id)
        logger.info(f"Successfully added label to card: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to add label to card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def add_member_to_card(ctx: Context, card_id: str, member_id: str) -> dict:
    """Adds a member to a card.

    Args:
        card_id (str): The ID of the card.
        member_id (str): The ID of the member to add.

    Returns:
        dict: The response from the add operation.
    """
    try:
        logger.info(f"Adding member {member_id} to card {card_id}")
        result = await service.add_member_to_card(card_id, member_id)
        logger.info(f"Successfully added member to card: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to add member to card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def delete_card(ctx: Context, card_id: str) -> dict:
    """Deletes a card.

    Args:
        card_id (str): The ID of the card to delete.

    Returns:
        dict: The response from the delete operation.
    """
    try:
        logger.info(f"Deleting card: {card_id}")
        result = await service.delete_card(card_id)
        logger.info(f"Successfully deleted card: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to delete card: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

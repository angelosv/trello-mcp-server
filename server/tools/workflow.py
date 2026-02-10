"""
Workflow tools for managing Trello cards - analyzing, moving, and updating cards.
"""
import logging
import re
from typing import List, Dict, Optional
from mcp.server.fastmcp import Context

from server.models import TrelloCard, TrelloList
from server.services.card import CardService
from server.services.list import ListService
from server.trello import client

logger = logging.getLogger(__name__)

card_service = CardService(client)
list_service = ListService(client)


def extract_priority(card: TrelloCard) -> str:
    """Extract priority from card description and labels."""
    # Primero verificar labels
    if card.labels:
        label_names = ' '.join([label.name.lower() for label in card.labels])
        if 'crítica' in label_names or 'critical' in label_names:
            return "CRÍTICA"
        elif 'alta' in label_names or 'high' in label_names:
            return "ALTA"
        elif 'media' in label_names or 'medium' in label_names:
            return "MEDIA"
        elif 'baja' in label_names or 'low' in label_names:
            return "BAJA"
    
    # Si no hay labels o no se encontró prioridad en labels, verificar descripción
    desc = card.desc or ""
    if not desc:
        return "MEDIA"
    
    desc_lower = desc.lower()
    if "prioridad: crítica" in desc_lower or "crítica" in desc_lower or "critical" in desc_lower:
        return "CRÍTICA"
    elif "prioridad: alta" in desc_lower or "alta" in desc_lower or "high" in desc_lower:
        return "ALTA"
    elif "prioridad: media" in desc_lower or "media" in desc_lower or "medium" in desc_lower:
        return "MEDIA"
    elif "prioridad: baja" in desc_lower or "baja" in desc_lower or "low" in desc_lower:
        return "BAJA"
    return "MEDIA"

    
    desc_lower = desc.lower()
    if "prioridad: crítica" in desc_lower or "crítica" in desc_lower or "critical" in desc_lower:
        return "CRÍTICA"
    elif "prioridad: alta" in desc_lower or "alta" in desc_lower or "high" in desc_lower:
        return "ALTA"
    elif "prioridad: media" in desc_lower or "media" in desc_lower or "medium" in desc_lower:
        return "MEDIA"
    elif "prioridad: baja" in desc_lower or "baja" in desc_lower or "low" in desc_lower:
        return "BAJA"
    return "MEDIA"


def is_engagement_related(name: str, desc: str) -> bool:
    """Check if card is related to Engagement."""
    text = (name + " " + (desc or "")).lower()
    return any(keyword in text for keyword in [
        "engagement", "poll", "contest", "vote", "participat"
    ])


async def analyze_developer_work(
    ctx: Context,
    board_id: str,
    doing_list_name: str = "Doing",
    done_list_name: str = "Done"
) -> Dict:
    """
    Analyzes cards in Doing and Done lists to see what the developer has worked on.
    
    Args:
        board_id: The ID of the Trello board
        doing_list_name: Name of the "Doing" list (default: "Doing")
        done_list_name: Name of the "Done" list (default: "Done")
    
    Returns:
        Dict with analysis results including cards in each list and summary
    """
    try:
        logger.info(f"Analyzing developer work in board: {board_id}")
        
        # Get all lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        doing_list = list_map.get(doing_list_name)
        done_list = list_map.get(done_list_name)
        
        if not doing_list:
            await ctx.error(f"List '{doing_list_name}' not found")
            return {"error": f"List '{doing_list_name}' not found"}
        
        if not done_list:
            await ctx.error(f"List '{done_list_name}' not found")
            return {"error": f"List '{done_list_name}' not found"}
        
        # Get cards from both lists
        doing_cards = await card_service.get_cards(doing_list.id)
        done_cards = await card_service.get_cards(done_list.id)
        
        result = {
            "doing": {
                "count": len(doing_cards),
                "cards": [{"id": c.id, "name": c.name, "url": c.url} for c in doing_cards]
            },
            "done": {
                "count": len(done_cards),
                "cards": [{"id": c.id, "name": c.name, "url": c.url} for c in done_cards]
            },
            "summary": {
                "total_in_progress": len(doing_cards),
                "total_completed": len(done_cards),
                "total": len(doing_cards) + len(done_cards)
            }
        }
        
        logger.info(f"Found {len(doing_cards)} cards in Doing, {len(done_cards)} in Done")
        return result
        
    except Exception as e:
        error_msg = f"Failed to analyze developer work: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def analyze_and_recommend_cards(
    ctx: Context,
    board_id: str,
    todo_list_name: str = "To do",
    backlog_list_name: str = "Backlog"
) -> Dict:
    """
    Analyzes cards in To do and Backlog and recommends which ones to work on this week.
    
    Args:
        board_id: The ID of the Trello board
        todo_list_name: Name of the "To do" list (default: "To do")
        backlog_list_name: Name of the "Backlog" list (default: "Backlog")
    
    Returns:
        Dict with recommendations organized by priority
    """
    try:
        logger.info(f"Analyzing and recommending cards in board: {board_id}")
        
        # Get all lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        todo_list = list_map.get(todo_list_name)
        backlog_list = list_map.get(backlog_list_name)
        
        if not todo_list:
            await ctx.error(f"List '{todo_list_name}' not found")
            return {"error": f"List '{todo_list_name}' not found"}
        
        if not backlog_list:
            await ctx.error(f"List '{backlog_list_name}' not found")
            return {"error": f"List '{backlog_list_name}' not found"}
        
        # Get cards from both lists
        todo_cards = await card_service.get_cards(todo_list.id)
        backlog_cards = await card_service.get_cards(backlog_list.id)
        
        # Get full card details to analyze
        all_cards = []
        
        for card in todo_cards:
            full_card = await card_service.get_card(card.id)
            desc = full_card.desc or ""
            priority = extract_priority(full_card)
            is_engagement = is_engagement_related(full_card.name, desc)
            
            all_cards.append({
                "id": full_card.id,
                "name": full_card.name,
                "url": full_card.url,
                "list": todo_list_name,
                "priority": priority,
                "is_engagement": is_engagement,
                "desc": desc[:200] if desc else ""
            })
        
        for card in backlog_cards:
            full_card = await card_service.get_card(card.id)
            desc = full_card.desc or ""
            priority = extract_priority(full_card)
            is_engagement = is_engagement_related(full_card.name, desc)
            
            all_cards.append({
                "id": full_card.id,
                "name": full_card.name,
                "url": full_card.url,
                "list": backlog_list_name,
                "priority": priority,
                "is_engagement": is_engagement,
                "desc": desc[:200] if desc else ""
            })
        
        # Categorize cards
        critical_engagement = [c for c in all_cards if c['priority'] == 'CRÍTICA' and c['is_engagement']]
        other_critical = [c for c in all_cards if c['priority'] == 'CRÍTICA' and not c['is_engagement']]
        high_engagement = [c for c in all_cards if c['priority'] == 'ALTA' and c['is_engagement']]
        
        recommendations = {
            "priority_1_critical_engagement": critical_engagement[:5],
            "priority_2_other_critical": other_critical[:3],
            "priority_3_high_engagement": high_engagement[:3],
            "summary": {
                "total_cards": len(all_cards),
                "critical_engagement": len(critical_engagement),
                "other_critical": len(other_critical),
                "high_engagement": len(high_engagement),
                "recommended_total": min(5, len(critical_engagement)) + min(3, len(other_critical)) + min(3, len(high_engagement))
            }
        }
        
        logger.info(f"Recommended {recommendations['summary']['recommended_total']} cards")
        return recommendations
        
    except Exception as e:
        error_msg = f"Failed to analyze and recommend cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def move_cards_by_priority(
    ctx: Context,
    board_id: str,
    from_list_name: str,
    to_list_name: str,
    priority_filter: Optional[str] = None,
    engagement_only: bool = False,
    limit: Optional[int] = None
) -> Dict:
    """
    Moves cards from one list to another based on priority and filters.
    
    Args:
        board_id: The ID of the Trello board
        from_list_name: Name of the source list
        to_list_name: Name of the destination list
        priority_filter: Filter by priority (CRÍTICA, ALTA, MEDIA, BAJA). If None, moves all.
        engagement_only: If True, only move Engagement-related cards
        limit: Maximum number of cards to move
    
    Returns:
        Dict with results of the move operation
    """
    try:
        logger.info(f"Moving cards from '{from_list_name}' to '{to_list_name}'")
        
        # Get lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        from_list = list_map.get(from_list_name)
        to_list = list_map.get(to_list_name)
        
        if not from_list:
            await ctx.error(f"List '{from_list_name}' not found")
            return {"error": f"List '{from_list_name}' not found"}
        
        if not to_list:
            await ctx.error(f"List '{to_list_name}' not found")
            return {"error": f"List '{to_list_name}' not found"}
        
        # Get cards from source list
        cards = await card_service.get_cards(from_list.id)
        
        # Filter cards
        cards_to_move = []
        for card in cards:
            full_card = await card_service.get_card(card.id)
            desc = full_card.desc or ""
            priority = extract_priority(full_card)
            is_engagement = is_engagement_related(full_card.name, desc)
            
            # Apply filters
            if priority_filter and priority != priority_filter:
                continue
            if engagement_only and not is_engagement:
                continue
            
            cards_to_move.append(full_card)
            
            if limit and len(cards_to_move) >= limit:
                break
        
        # Move cards
        moved = []
        failed = []
        
        for card in cards_to_move:
            try:
                await card_service.update_card(card.id, idList=to_list.id)
                moved.append({"id": card.id, "name": card.name})
                logger.info(f"Moved card: {card.name}")
            except Exception as e:
                failed.append({"id": card.id, "name": card.name, "error": str(e)})
                logger.error(f"Failed to move card {card.id}: {e}")
        
        result = {
            "moved": moved,
            "failed": failed,
            "summary": {
                "total_found": len(cards),
                "total_moved": len(moved),
                "total_failed": len(failed)
            }
        }
        
        logger.info(f"Moved {len(moved)} cards successfully")
        return result
        
    except Exception as e:
        error_msg = f"Failed to move cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def update_card_description(
    ctx: Context,
    card_id: str,
    new_description: str
) -> TrelloCard:
    """
    Updates the description of a card.
    
    Args:
        card_id: The ID of the card to update
        new_description: The new description text
    
    Returns:
        The updated TrelloCard
    """
    try:
        logger.info(f"Updating description for card: {card_id}")
        result = await card_service.update_card(card_id, desc=new_description)
        logger.info(f"Successfully updated card description: {card_id}")
        return result
    except Exception as e:
        error_msg = f"Failed to update card description: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def move_critical_cards_to_todo(
    ctx: Context,
    board_id: str,
    backlog_list_name: str = "Backlog",
    todo_list_name: str = "To do"
) -> Dict:
    """
    Automatically moves critical and high-priority cards from Backlog to To do.
    
    Args:
        board_id: The ID of the Trello board
        backlog_list_name: Name of the Backlog list
        todo_list_name: Name of the To do list
    
    Returns:
        Dict with results of the move operation
    """
    try:
        logger.info("Moving critical cards from Backlog to To do")
        
        # Move critical cards
        critical_result = await move_cards_by_priority(
            ctx, board_id, backlog_list_name, todo_list_name,
            priority_filter="CRÍTICA", engagement_only=False
        )
        
        # Move high-priority engagement cards
        high_engagement_result = await move_cards_by_priority(
            ctx, board_id, backlog_list_name, todo_list_name,
            priority_filter="ALTA", engagement_only=True
        )
        
        return {
            "critical_moved": critical_result.get("moved", []),
            "high_engagement_moved": high_engagement_result.get("moved", []),
            "summary": {
                "critical_moved": len(critical_result.get("moved", [])),
                "high_engagement_moved": len(high_engagement_result.get("moved", [])),
                "total_moved": len(critical_result.get("moved", [])) + len(high_engagement_result.get("moved", []))
            }
        }
        
    except Exception as e:
        error_msg = f"Failed to move critical cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_backlog_cards_sorted_by_priority(
    ctx: Context,
    board_id: str,
    backlog_list_name: str = "Backlog"
) -> Dict:
    """
    Gets all cards from the Backlog list sorted by priority (CRÍTICA > ALTA > MEDIA > BAJA).
    
    Args:
        board_id: The ID of the Trello board
        backlog_list_name: Name of the Backlog list (default: "Backlog")
    
    Returns:
        Dict with cards sorted by priority
    """
    try:
        logger.info(f"Getting backlog cards sorted by priority in board: {board_id}")
        
        # Get lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        backlog_list = list_map.get(backlog_list_name)
        if not backlog_list:
            await ctx.error(f"List '{backlog_list_name}' not found")
            return {"error": f"List '{backlog_list_name}' not found"}
        
        # Get cards from backlog
        cards = await card_service.get_cards(backlog_list.id)
        
        # Get full card details and extract priority
        cards_with_priority = []
        for card in cards:
            full_card = await card_service.get_card(card.id)
            priority = extract_priority(full_card)
            cards_with_priority.append({
                "card": full_card,
                "priority": priority
            })
        
        # Sort by priority (CRÍTICA > ALTA > MEDIA > BAJA)
        priority_order = {"CRÍTICA": 0, "ALTA": 1, "MEDIA": 2, "BAJA": 3}
        cards_with_priority.sort(key=lambda x: priority_order.get(x["priority"], 2))
        
        result = {
            "cards": [
                {
                    "id": item["card"].id,
                    "name": item["card"].name,
                    "url": item["card"].url,
                    "priority": item["priority"],
                    "labels": [{"name": label.name, "color": label.color} for label in item["card"].labels],
                    "desc": item["card"].desc[:200] if item["card"].desc else ""
                }
                for item in cards_with_priority
            ],
            "summary": {
                "total": len(cards_with_priority),
                "by_priority": {
                    "CRÍTICA": len([c for c in cards_with_priority if c["priority"] == "CRÍTICA"]),
                    "ALTA": len([c for c in cards_with_priority if c["priority"] == "ALTA"]),
                    "MEDIA": len([c for c in cards_with_priority if c["priority"] == "MEDIA"]),
                    "BAJA": len([c for c in cards_with_priority if c["priority"] == "BAJA"])
                }
            }
        }
        
        logger.info(f"Found {len(cards_with_priority)} cards in backlog")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get backlog cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def move_backlog_to_todo_by_priority(
    ctx: Context,
    board_id: str,
    backlog_list_name: str = "Backlog",
    todo_list_name: str = "To do",
    limit: Optional[int] = None
) -> Dict:
    """
    Moves cards from Backlog to To do list, sorted by priority (highest priority first).
    
    Args:
        board_id: The ID of the Trello board
        backlog_list_name: Name of the Backlog list (default: "Backlog")
        todo_list_name: Name of the To do list (default: "To do")
        limit: Maximum number of cards to move (default: None, moves all)
    
    Returns:
        Dict with results of the move operation
    """
    try:
        logger.info(f"Moving backlog cards to To do by priority in board: {board_id}")
        
        # Get backlog cards sorted by priority
        backlog_result = await get_backlog_cards_sorted_by_priority(ctx, board_id, backlog_list_name)
        if "error" in backlog_result:
            return backlog_result
        
        # Get todo list
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        todo_list = list_map.get(todo_list_name)
        
        if not todo_list:
            await ctx.error(f"List '{todo_list_name}' not found")
            return {"error": f"List '{todo_list_name}' not found"}
        
        # Move cards up to limit
        cards_to_move = backlog_result["cards"][:limit] if limit else backlog_result["cards"]
        
        moved = []
        failed = []
        
        for card_info in cards_to_move:
            try:
                await card_service.update_card(card_info["id"], idList=todo_list.id)
                moved.append({"id": card_info["id"], "name": card_info["name"], "priority": card_info["priority"]})
                logger.info(f"Moved card: {card_info['name']} (Priority: {card_info['priority']})")
            except Exception as e:
                failed.append({"id": card_info["id"], "name": card_info["name"], "error": str(e)})
                logger.error(f"Failed to move card {card_info['id']}: {e}")
        
        result = {
            "moved": moved,
            "failed": failed,
            "summary": {
                "total_found": len(backlog_result["cards"]),
                "total_moved": len(moved),
                "total_failed": len(failed)
            }
        }
        
        logger.info(f"Moved {len(moved)} cards successfully")
        return result
        
    except Exception as e:
        error_msg = f"Failed to move backlog cards: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def analyze_developer_work_with_comments(
    ctx: Context,
    board_id: str,
    doing_list_name: str = "Doing",
    done_list_name: str = "Done"
) -> Dict:
    """
    Analyzes cards in Doing and Done lists including comments/actions.
    
    Args:
        board_id: The ID of the Trello board
        doing_list_name: Name of the "Doing" list (default: "Doing")
        done_list_name: Name of the "Done" list (default: "Done")
    
    Returns:
        Dict with analysis results including cards and their comments
    """
    try:
        logger.info(f"Analyzing developer work with comments in board: {board_id}")
        
        # Get all lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        doing_list = list_map.get(doing_list_name)
        done_list = list_map.get(done_list_name)
        
        if not doing_list:
            await ctx.error(f"List '{doing_list_name}' not found")
            return {"error": f"List '{doing_list_name}' not found"}
        
        if not done_list:
            await ctx.error(f"List '{done_list_name}' not found")
            return {"error": f"List '{done_list_name}' not found"}
        
        # Get cards from both lists
        doing_cards = await card_service.get_cards(doing_list.id)
        done_cards = await card_service.get_cards(done_list.id)
        
        # Get full details including comments
        def get_card_with_comments(card):
            return {
                "id": card.id,
                "name": card.name,
                "url": card.url,
                "desc": card.desc[:200] if card.desc else "",
                "labels": [{"name": label.name, "color": label.color} for label in card.labels]
            }
        
        doing_cards_details = []
        for card in doing_cards:
            full_card = await card_service.get_card(card.id)
            card_info = get_card_with_comments(full_card)
            # Get comments
            try:
                actions = await card_service.get_card_actions(card.id, filter_type="commentCard")
                card_info["comments"] = [
                    {
                        "text": action.get("data", {}).get("text", ""),
                        "date": action.get("date", ""),
                        "member": action.get("memberCreator", {}).get("fullName", "Unknown")
                    }
                    for action in actions
                ]
            except Exception as e:
                logger.warning(f"Could not fetch comments for card {card.id}: {e}")
                card_info["comments"] = []
            doing_cards_details.append(card_info)
        
        done_cards_details = []
        for card in done_cards:
            full_card = await card_service.get_card(card.id)
            card_info = get_card_with_comments(full_card)
            # Get comments
            try:
                actions = await card_service.get_card_actions(card.id, filter_type="commentCard")
                card_info["comments"] = [
                    {
                        "text": action.get("data", {}).get("text", ""),
                        "date": action.get("date", ""),
                        "member": action.get("memberCreator", {}).get("fullName", "Unknown")
                    }
                    for action in actions
                ]
            except Exception as e:
                logger.warning(f"Could not fetch comments for card {card.id}: {e}")
                card_info["comments"] = []
            done_cards_details.append(card_info)
        
        result = {
            "doing": {
                "count": len(doing_cards_details),
                "cards": doing_cards_details
            },
            "done": {
                "count": len(done_cards_details),
                "cards": done_cards_details
            },
            "summary": {
                "total_in_progress": len(doing_cards_details),
                "total_completed": len(done_cards_details),
                "total": len(doing_cards_details) + len(done_cards_details)
            }
        }
        
        logger.info(f"Found {len(doing_cards_details)} cards in Doing, {len(done_cards_details)} in Done")
        return result
        
    except Exception as e:
        error_msg = f"Failed to analyze developer work with comments: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_list_cards_with_details(
    ctx: Context,
    board_id: str,
    list_name: str
) -> Dict:
    """
    Gets all cards from a list with comprehensive details including labels, descriptions, and comments.
    
    Args:
        board_id: The ID of the Trello board
        list_name: Name of the list
    
    Returns:
        Dict with cards and their details
    """
    try:
        logger.info(f"Getting cards with details from list '{list_name}' in board: {board_id}")
        
        # Get lists
        lists = await list_service.get_lists(board_id)
        list_map = {lst.name: lst for lst in lists}
        
        target_list = list_map.get(list_name)
        if not target_list:
            await ctx.error(f"List '{list_name}' not found")
            return {"error": f"List '{list_name}' not found"}
        
        # Get cards from list
        cards = await card_service.get_cards(target_list.id)
        
        # Get full details for each card
        cards_details = []
        for card in cards:
            full_card = await card_service.get_card(card.id)
            priority = extract_priority(full_card)
            
            card_info = {
                "id": full_card.id,
                "name": full_card.name,
                "url": full_card.url,
                "desc": full_card.desc or "",
                "priority": priority,
                "labels": [{"name": label.name, "color": label.color} for label in full_card.labels],
                "due": full_card.due,
                "pos": full_card.pos
            }
            
            # Get comments
            try:
                actions = await card_service.get_card_actions(full_card.id, filter_type="commentCard")
                card_info["comments"] = [
                    {
                        "text": action.get("data", {}).get("text", ""),
                        "date": action.get("date", ""),
                        "member": action.get("memberCreator", {}).get("fullName", "Unknown")
                    }
                    for action in actions
                ]
            except Exception as e:
                logger.warning(f"Could not fetch comments for card {full_card.id}: {e}")
                card_info["comments"] = []
            
            cards_details.append(card_info)
        
        result = {
            "list_name": list_name,
            "cards": cards_details,
            "summary": {
                "total": len(cards_details),
                "by_priority": {
                    "CRÍTICA": len([c for c in cards_details if c["priority"] == "CRÍTICA"]),
                    "ALTA": len([c for c in cards_details if c["priority"] == "ALTA"]),
                    "MEDIA": len([c for c in cards_details if c["priority"] == "MEDIA"]),
                    "BAJA": len([c for c in cards_details if c["priority"] == "BAJA"])
                }
            }
        }
        
        logger.info(f"Found {len(cards_details)} cards in list '{list_name}'")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get list cards with details: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

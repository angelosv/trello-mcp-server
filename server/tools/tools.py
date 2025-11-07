"""
This module contains tools for managing Trello boards, lists, and cards.
"""

from server.tools import board, card, checklist, list
from server.tools import smart_card, card_review


def register_tools(mcp):
    """Register tools with the MCP server."""
    # Board Tools
    mcp.add_tool(board.get_board)
    mcp.add_tool(board.get_boards)
    mcp.add_tool(board.get_board_labels)
    mcp.add_tool(board.get_board_members)
    mcp.add_tool(board.create_board_label)

    # List Tools
    mcp.add_tool(list.get_list)
    mcp.add_tool(list.get_lists)
    mcp.add_tool(list.create_list)
    mcp.add_tool(list.update_list)
    mcp.add_tool(list.delete_list)

    # Card Tools
    mcp.add_tool(card.get_card)
    mcp.add_tool(card.get_cards)
    mcp.add_tool(card.create_card)
    mcp.add_tool(card.update_card)
    mcp.add_tool(card.add_label_to_card)
    mcp.add_tool(card.add_member_to_card)
    mcp.add_tool(card.delete_card)

    # Smart Card Tools (análisis inteligente antes de crear tarjetas)
    mcp.add_tool(smart_card.create_smart_card_from_commit)
    mcp.add_tool(smart_card.create_smart_cards_from_recent_commits)
    mcp.add_tool(smart_card.analyze_file_for_kotlin)
    
    # Card Review Tools (revisar y actualizar tarjetas existentes)
    mcp.add_tool(card_review.review_cards_for_updates)
    mcp.add_tool(card_review.get_available_members_for_assignment)
    mcp.add_tool(card_review.suggest_members_for_commit)

    # Checklist Tools
    mcp.add_tool(checklist.get_checklist)
    mcp.add_tool(checklist.get_card_checklists)
    mcp.add_tool(checklist.create_checklist)
    mcp.add_tool(checklist.update_checklist)
    mcp.add_tool(checklist.delete_checklist)
    mcp.add_tool(checklist.add_checkitem)
    mcp.add_tool(checklist.update_checkitem)
    mcp.add_tool(checklist.delete_checkitem)

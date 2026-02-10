"""
This module contains tools for managing Trello boards, lists, and cards.
"""

from server.tools import board, card, checklist, list
from server.tools import smart_card, card_review, code_review, workflow


def register_tools(mcp):
    """Register tools with the MCP server."""
    # Board Tools
    mcp.add_tool(board.get_board)
    mcp.add_tool(board.get_boards)
    mcp.add_tool(board.list_all_boards)
    mcp.add_tool(board.get_board_labels)
    mcp.add_tool(board.get_board_members)
    mcp.add_tool(board.create_board)
    mcp.add_tool(board.create_board_with_tasks)
    mcp.add_tool(board.create_tasks_in_board)
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

    # Code Review Tools (revisar código Kotlin implementado)
    mcp.add_tool(code_review.review_kotlin_implementation)

    # Checklist Tools
    mcp.add_tool(checklist.get_checklist)
    mcp.add_tool(checklist.get_card_checklists)
    mcp.add_tool(checklist.create_checklist)
    mcp.add_tool(checklist.update_checklist)
    mcp.add_tool(checklist.delete_checklist)
    mcp.add_tool(checklist.add_checkitem)
    mcp.add_tool(checklist.update_checkitem)
    mcp.add_tool(checklist.delete_checkitem)

    # Workflow Tools (card management and analysis)
    mcp.add_tool(workflow.analyze_developer_work)
    mcp.add_tool(workflow.analyze_and_recommend_cards)
    mcp.add_tool(workflow.move_cards_by_priority)
    mcp.add_tool(workflow.update_card_description)
    mcp.add_tool(workflow.move_critical_cards_to_todo)
    mcp.add_tool(workflow.get_backlog_cards_sorted_by_priority)
    mcp.add_tool(workflow.move_backlog_to_todo_by_priority)
    mcp.add_tool(workflow.analyze_developer_work_with_comments)
    mcp.add_tool(workflow.get_list_cards_with_details)

#!/usr/bin/env python3
"""
Script to create all Viaplay production implementation cards in Trello.
This script creates cards with checklists and labels based on the task list.
"""

import asyncio
import os
import sys
from typing import Dict, List, Optional

# Add parent directory to path to import server modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from server.services.board import BoardService
from server.services.list import ListService
from server.services.card import CardService
from server.services.checklist import ChecklistService
from server.utils.trello_api import TrelloClient

# Load environment variables
load_dotenv()

# Initialize Trello client
api_key = os.getenv("TRELLO_API_KEY")
token = os.getenv("TRELLO_TOKEN")
if not api_key or not token:
    raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN must be set")

client = TrelloClient(api_key=api_key, token=token)
board_service = BoardService(client)
list_service = ListService(client)
card_service = CardService(client)
checklist_service = ChecklistService(client)

BOARD_ID = "697341164d92cf9e79c30887"

# Tag to label color mapping
TAG_COLOR_MAP = {
    "backend": "red",
    "swift": "blue",
    "kotlin": "green",
    "sdk": "orange",
    "database": "purple",
    "api": "pink",
    "websocket": "yellow",
    "ui": "sky",
    "network": "lime",
    "realtime": "black",
    "timeline": "red",
    "chat": "blue",
    "polls": "green",
    "video": "orange",
    "integration": "purple",
    "auth": "pink",
    "admin": "yellow",
    "demo": "sky",
    "migration": "lime",
    "setup": "black",
    "configuration": "red",
    "documentation": "blue",
    "testing": "green",
    "priority-high": "red",
    "priority-medium": "yellow",
    "priority-low": "green",
}


async def get_or_create_label(board_id: str, tag: str) -> Optional[str]:
    """Get or create a label for a tag. Returns label ID."""
    try:
        # Get all labels for the board
        labels = await board_service.get_board_labels(board_id)
        
        # Find existing label with this name
        for label in labels:
            if label.name and label.name.lower() == tag.lower():
                return label.id
        
        # Create new label if not found
        color = TAG_COLOR_MAP.get(tag.lower(), "grey")
        label_data = await client.POST(f"/labels", data={
            "name": tag,
            "color": color,
            "idBoard": board_id,
        })
        return label_data["id"]
    except Exception as e:
        print(f"Error getting/creating label for {tag}: {e}")
        return None


async def create_card_with_checklist(
    list_id: str,
    name: str,
    desc: str,
    checklist_items: List[str],
    label_ids: List[str],
) -> Optional[str]:
    """Create a card with checklist and labels. Returns card ID."""
    try:
        # Create card
        card = await card_service.create_card(
            idList=list_id,
            name=name,
            desc=desc,
            idLabels=",".join(label_ids) if label_ids else None,
        )
        card_id = card.id
        
        # Create checklist if there are items
        if checklist_items:
            checklist = await checklist_service.create_checklist(card_id, "Checklist")
            checklist_id = checklist["id"]
            
            # Add checklist items
            for item in checklist_items:
                await checklist_service.add_checkitem(checklist_id, item)
        
        return card_id
    except Exception as e:
        print(f"Error creating card {name}: {e}")
        return None


# Task definitions - Module 1: Backend - Database Schema
MODULE_1_TASKS = [
    {
        "name": "CARD 1.1: Create Matches Table",
        "desc": "Create PostgreSQL table to store match information\n\nEstimation: 1 day\nTags: backend, database, postgresql, schema, priority-high",
        "checklist": [
            "Create matches table with columns: id, home_team, away_team, start_time, status, video_stream_url",
            "Add indexes on id and status",
            "Create migration file",
            "Add seed data for testing",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "schema", "priority-high"],
    },
    {
        "name": "CARD 1.2: Create Timeline Events Table",
        "desc": "Create table to store timeline events synchronized with video\n\nEstimation: 1 day\nTags: backend, database, postgresql, schema, priority-high",
        "checklist": [
            "Create timeline_events table with columns: id, match_id, event_type, video_timestamp, data (JSONB), created_at",
            "Add foreign key constraint to matches table",
            "Add indexes on match_id, video_timestamp, event_type",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "schema", "priority-high"],
    },
    {
        "name": "CARD 1.3: Create Event Types Table",
        "desc": "Create table to store event type definitions and configurations\n\nEstimation: 1 day\nTags: backend, database, postgresql, schema, priority-medium",
        "checklist": [
            "Create event_types table with columns: id, name, category, display_config (JSONB)",
            "Add seed data for all event types (goal, card, substitution, chat, poll, etc.)",
            "Create migration file",
            "Document event types",
        ],
        "tags": ["backend", "database", "postgresql", "schema", "priority-medium"],
    },
    {
        "name": "CARD 1.4: Create Match Phases Table",
        "desc": "Create table to track match phases (pre-match, first half, halftime, etc.)\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, schema, priority-medium",
        "checklist": [
            "Create match_phases table with columns: id, match_id, phase_type, start_timestamp, end_timestamp",
            "Add foreign key to matches table",
            "Create migration file",
            "Document phases",
        ],
        "tags": ["backend", "database", "postgresql", "schema", "priority-medium"],
    },
    {
        "name": "CARD 1.5: Create Chat Messages Table",
        "desc": "Create table to store chat messages\n\nEstimation: 1 day\nTags: backend, database, postgresql, chat, priority-high",
        "checklist": [
            "Create chat_messages table with columns: id, match_id, user_id, username, message, likes, created_at",
            "Add indexes on match_id and created_at",
            "Add foreign key to matches table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "chat", "priority-high"],
    },
    {
        "name": "CARD 1.6: Create Chat Users Table",
        "desc": "Create table to store chat user information\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, chat, priority-high",
        "checklist": [
            "Create chat_users table with columns: id, username, display_name, avatar_url, role",
            "Add index on username",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "chat", "priority-high"],
    },
    {
        "name": "CARD 1.7: Create Message Moderation Table",
        "desc": "Create table to track message moderation status\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, moderation, priority-medium",
        "checklist": [
            "Create message_moderation table with columns: message_id, status, moderated_by, reason, moderated_at",
            "Add foreign key to chat_messages table",
            "Create migration file",
            "Document moderation workflow",
        ],
        "tags": ["backend", "database", "postgresql", "moderation", "priority-medium"],
    },
    {
        "name": "CARD 1.8: Create Polls Table",
        "desc": "Create table to store polls and quizzes\n\nEstimation: 1 day\nTags: backend, database, postgresql, polls, priority-high",
        "checklist": [
            "Create polls table with columns: id, match_id, question, type, start_time, end_time, video_timestamp",
            "Add indexes on match_id and video_timestamp",
            "Add foreign key to matches table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "polls", "priority-high"],
    },
    {
        "name": "CARD 1.9: Create Poll Options Table",
        "desc": "Create table to store poll options\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, polls, priority-high",
        "checklist": [
            "Create poll_options table with columns: id, poll_id, text, is_correct (for quizzes)",
            "Add foreign key to polls table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "polls", "priority-high"],
    },
    {
        "name": "CARD 1.10: Create Poll Responses Table",
        "desc": "Create table to store user poll responses\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, polls, priority-high",
        "checklist": [
            "Create poll_responses table with columns: id, poll_id, user_id, option_id, responded_at",
            "Add unique constraint on (poll_id, user_id) to prevent duplicate votes",
            "Add indexes on poll_id and user_id",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "polls", "priority-high"],
    },
    {
        "name": "CARD 1.11: Create Contests Table",
        "desc": "Create table to store contests/giveaways\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, contests, priority-medium",
        "checklist": [
            "Create contests table with columns: id, match_id, title, description, prize, draw_time, video_timestamp",
            "Add foreign key to matches table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "contests", "priority-medium"],
    },
    {
        "name": "CARD 1.12: Create Contest Participants Table",
        "desc": "Create table to track contest participants\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, contests, priority-medium",
        "checklist": [
            "Create contest_participants table with columns: id, contest_id, user_id, participated_at",
            "Add unique constraint on (contest_id, user_id)",
            "Add indexes on contest_id and user_id",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "contests", "priority-medium"],
    },
    {
        "name": "CARD 1.13: Create Highlights Table",
        "desc": "Create table to store match highlights\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, highlights, priority-medium",
        "checklist": [
            "Create highlights table with columns: id, match_id, title, video_url, thumbnail_url, duration, video_timestamp, event_type",
            "Add indexes on match_id and video_timestamp",
            "Add foreign key to matches table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "highlights", "priority-medium"],
    },
    {
        "name": "CARD 1.14: Create Match Statistics Table",
        "desc": "Create table to store match statistics\n\nEstimation: 0.5 days\nTags: backend, database, postgresql, statistics, priority-medium",
        "checklist": [
            "Create match_statistics table with columns: id, match_id, timestamp, possession_home, possession_away, shots_home, shots_away, corners_home, corners_away",
            "Add indexes on match_id and timestamp",
            "Add foreign key to matches table",
            "Create migration file",
            "Document table schema",
        ],
        "tags": ["backend", "database", "postgresql", "statistics", "priority-medium"],
    },
]


async def main():
    """Main function to create all cards."""
    print("Starting card creation process...")
    
    # Get lists for the board
    print(f"Getting lists for board {BOARD_ID}...")
    lists = await list_service.get_lists(BOARD_ID)
    
    # Find "backlog" list
    backlog_list = None
    for lst in lists:
        if lst.name.lower() == "backlog":
            backlog_list = lst
            break
    
    if not backlog_list:
        print("ERROR: Could not find 'backlog' list!")
        print(f"Available lists: {[lst.name for lst in lists]}")
        return
    
    print(f"Found backlog list: {backlog_list.name} (ID: {backlog_list.id})")
    
    # Get or create labels for all tags
    print("Getting/creating labels...")
    tag_to_label_id: Dict[str, str] = {}
    all_tags = set()
    for task in MODULE_1_TASKS:
        all_tags.update(task["tags"])
    
    for tag in all_tags:
        label_id = await get_or_create_label(BOARD_ID, tag)
        if label_id:
            tag_to_label_id[tag] = label_id
            print(f"  Label '{tag}': {label_id}")
    
    # Create cards
    print(f"\nCreating {len(MODULE_1_TASKS)} cards...")
    created_count = 0
    for i, task in enumerate(MODULE_1_TASKS, 1):
        print(f"\n[{i}/{len(MODULE_1_TASKS)}] Creating: {task['name']}")
        
        # Get label IDs for this task
        label_ids = [tag_to_label_id[tag] for tag in task["tags"] if tag in tag_to_label_id]
        
        # Create card with checklist
        card_id = await create_card_with_checklist(
            list_id=backlog_list.id,
            name=task["name"],
            desc=task["desc"],
            checklist_items=task["checklist"],
            label_ids=label_ids,
        )
        
        if card_id:
            created_count += 1
            print(f"  Created card ID: {card_id}")
        else:
            print(f"  Failed to create card")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    print(f"\n\nCompleted! Created {created_count}/{len(MODULE_1_TASKS)} cards.")
    
    # Close client
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())

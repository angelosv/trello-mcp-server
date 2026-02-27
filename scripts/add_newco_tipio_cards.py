#!/usr/bin/env python3
"""
Add cards to Newco/Tipio board:
1. Doing: Completed work (rebrand, demo refactor, docs) since Thursday
2. Todos: Hardcoded MVP frontend tasks
"""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

BOARD_ID = "697341164d92cf9e79c30887"  # Newco/Tipio
DOING_LIST_ID = "69734129f4e58737d9b6743c"
TODOS_LIST_ID = "6973412761295592a293da58"


def get_labels(board_id):
    r = httpx.get(
        f"{TRELLO_API_BASE}/boards/{board_id}/labels",
        params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
    )
    r.raise_for_status()
    return {lb.get("name", "").lower(): lb["id"] for lb in r.json() if lb.get("name")}


def find_label(labels, *names):
    for n in names:
        lid = labels.get(n.lower())
        if lid:
            return lid
    return None


def create_card(list_id, name, desc, label_ids=None):
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": name,
        "desc": desc,
    }
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    r = httpx.post(f"{TRELLO_API_BASE}/cards", params=params)
    r.raise_for_status()
    return r.json()


def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Configura TRELLO_API_KEY y TRELLO_TOKEN en .env")
        sys.exit(1)

    labels = get_labels(BOARD_ID)
    swift_lb = find_label(labels, "swift", "sdk")
    rebrand_lb = find_label(labels, "rebrand")
    doc_lb = find_label(labels, "documentation")
    demo_lb = find_label(labels, "demo")
    backend_lb = find_label(labels, "backend")

    doing_labels = [x for x in [swift_lb, rebrand_lb, doc_lb, demo_lb] if x]
    todos_labels = [x for x in [backend_lb] if x]

    # --- DOING: Completed work since Thursday ---
    doing_cards = [
        (
            "Viaplay Demo: Engagement Components Refactor (Completed)",
            """## Viaplay Demo: Engagement Components Refactor

**Estimation:** Completed (Jan 23-24, 2026)
**Tags:** Swift, SDK, Demo, Refactor

### Summary
Removed duplicated engagement components from Viaplay Demo. Demo now consumes all engagement UI from VioCastingUI.

### Changes completed
- **Removed from Demo:** Chat (ChatAvatar, ChatInputBar, ChatListView, ChatMessageRow), Match (AllContentFeed, MatchHeaderView, MatchScoreView, etc.), Polls (PollCard, PollsListView, etc.), Products (CastingProductCard, CastingProductModal), Timeline (TimelineEventCard, HighlightCard, etc.), Statistics (StatBar, StatPreviewCard), Social (AdminCommentCard, TweetCard)
- **Removed Managers:** ChatManager, LiveMatchViewModel, MatchSimulationManager, TimelineDataGenerator, UnifiedTimelineManager, UserParticipationManager
- **Removed Models:** ChatModels, MatchStatisticsModels, TimelineEventModels, TimelineEventProtocol
- **SportDetailView** now uses `LiveMatchView` from VioCastingUI
- **Kept in Demo:** Layout components only (HeroSection, CategoryCard, RentBuyCard, ViaplayOfferBannerView, CampaignSponsorBadge, CachedAsyncImage)

### Files affected
- Demo/Viaplay/Viaplay/Components/ (60+ files removed)
- Demo/Viaplay/Viaplay/Managers/
- Demo/Viaplay/Viaplay/Models/
- SportDetailView.swift, ViaplayApp.swift, ViaplayHomeView.swift
""",
        ),
        (
            "CacheHelper Migration to VioDesignSystem (Completed)",
            """## CacheHelper Migration to VioDesignSystem

**Estimation:** Completed (Jan 23, 2026)
**Tags:** Swift, SDK, Demo

### Summary
Moved CacheHelper from Demo to VioDesignSystem for reuse across SDK consumers.

### Changes completed
- Created `Sources/VioDesignSystem/Helpers/CacheHelper.swift` with public API
- Exported `VioCacheHelper` in VioDesignSystem.swift
- Updated ViaplayApp with `import VioDesignSystem`
- Removed Demo's `Helpers/CacheHelper.swift`

### Files affected
- Sources/VioDesignSystem/Helpers/CacheHelper.swift (new)
- Sources/VioDesignSystem/VioDesignSystem.swift
- Demo/Viaplay/Viaplay/ViaplayApp.swift
""",
        ),
        (
            "Demo Documentation Consolidation (Completed)",
            """## Demo Documentation Consolidation

**Estimation:** Completed (Jan 23, 2026)
**Tags:** Swift, SDK, Documentation

### Summary
Cleaned up and consolidated documentation in Demo/Viaplay/ and Documentation/.

### Deleted (obsolete)
- CURRENT_STATUS.md, LOGIC_SEPARATION.md, REFACTORING_COMPLETE.md
- TIMELINE_SYSTEM.md, TIMELINE_SYNC_PLAN.md, TIMELINE_ARCHITECTURE.md
- QUICK_START.md, USAGE_MATCH_CONTEXT.md
- DEMO_DATA_INTEGRATION_GUIDE.md, DEMO_NOTES.md, PROJECT_MASTER_DOCUMENTATION.md

### Created/Moved
- **Documentation/BROADCAST_CONTEXT_GUIDE.md** – Broadcast context and auto-discovery (from USAGE_MATCH_CONTEXT)
- **Demo/Viaplay/README.md** – Single consolidated README (architecture, DemoDataManager, config, troubleshooting)

### Acceptance criteria
- [x] Single README for Demo
- [x] No obsolete references to removed components
- [x] Broadcast context in SDK docs
""",
        ),
        (
            "Viaplay Delivery Package: Exclusion List (Completed)",
            """## Viaplay Delivery Package: Exclusion List

**Estimation:** Completed (Jan 23, 2026)
**Tags:** Swift, SDK, Documentation

### Summary
Documented which files should NOT be included when sending a version to Viaplay development team.

### Exclusions
- **Other demos:** Demo/tv2demo/, Demo/Vg/, Demo/ReachuDemoApp/
- **Internal docs:** BACKEND_API_SPEC, BACKEND_IMPLEMENTATION_GUIDE, BACKEND_QA_RESPONSES, VIDEO_SYNC_API_SPEC, COMPONENTIZATION_REFERENCE
- **Scripts:** generate_app_icons.sh
- **Config:** Replace real API keys in vio-config.json with placeholders before sending

### Included
- Sources/, Package.swift, README.md
- Demo/Viaplay/ (with placeholder config)
- Documentation/BROADCAST_CONTEXT_GUIDE.md
""",
        ),
    ]

    # --- TODOS: Dashboard MVP (Hardcoded Frontend) ---
    todos_cards = [
        (
            "MVP.1: Setup Dashboard Project Structure",
            """Initialize dashboard project (React/Next.js or similar)

**Estimation:** 1 day
**Tags:** backend, dashboard, frontend, mvp, priority-high

### Scope
- Create project structure for admin dashboard
- Add routing, basic layout (sidebar, header)
- Hardcoded/mock data - no API calls yet

### Acceptance criteria
- [ ] Dashboard app runs locally
- [ ] Basic layout with navigation
- [ ] No backend dependency
""",
        ),
        (
            "MVP.2: Create Matches List Screen (Hardcoded)",
            """Create matches list with hardcoded data

**Estimation:** 1 day
**Tags:** backend, dashboard, frontend, mvp, priority-high

### Scope
- Table/list of matches (hardcoded)
- Columns: home team, away team, date, status
- Click to navigate to match detail

### Acceptance criteria
- [ ] Matches list displays hardcoded data
- [ ] Basic table styling
- [ ] Navigation to match detail
""",
        ),
        (
            "MVP.3: Create Match Detail Screen (Hardcoded)",
            """Create match detail screen with tabs

**Estimation:** 2 days
**Tags:** backend, dashboard, frontend, mvp, priority-high

### Scope
- Match detail screen with tabs: Timeline | Chat | Polls | Statistics
- Hardcoded match data
- Tab navigation (no content yet)

### Acceptance criteria
- [ ] Match detail shows match info
- [ ] Tabs for Timeline, Chat, Polls, Statistics
- [ ] Tab switching works
""",
        ),
        (
            "MVP.4: Create Timeline Events List (Hardcoded)",
            """Create timeline events management UI

**Estimation:** 2 days
**Tags:** backend, dashboard, frontend, timeline, mvp, priority-high

### Scope
- List of timeline events (hardcoded)
- Columns: minute, type, description
- Add/Edit/Delete buttons (UI only, no API)

### Acceptance criteria
- [ ] Timeline events list displays hardcoded data
- [ ] Form for add/edit (no submit to API)
- [ ] Basic CRUD UI
""",
        ),
        (
            "MVP.5: Create Chat Messages List (Hardcoded)",
            """Create chat moderation UI

**Estimation:** 1.5 days
**Tags:** backend, dashboard, frontend, chat, mvp, priority-high

### Scope
- List of chat messages (hardcoded)
- Columns: user, message, time, status
- Moderate/Delete buttons (UI only)

### Acceptance criteria
- [ ] Chat list displays hardcoded messages
- [ ] Moderate/Delete UI (no API)
- [ ] Basic filtering
""",
        ),
        (
            "MVP.6: Create Polls List (Hardcoded)",
            """Create polls management UI

**Estimation:** 1.5 days
**Tags:** backend, dashboard, frontend, polls, mvp, priority-high

### Scope
- List of polls (hardcoded)
- Create poll form (UI only)
- Add options, set duration (no API)

### Acceptance criteria
- [ ] Polls list displays hardcoded data
- [ ] Create poll form (no submit)
- [ ] Options editor UI
""",
        ),
        (
            "MVP.7: Create Statistics View (Hardcoded)",
            """Create match statistics display

**Estimation:** 1 day
**Tags:** backend, dashboard, frontend, statistics, mvp, priority-medium

### Scope
- Statistics display (possession, shots, etc.)
- Hardcoded values
- Basic charts or tables

### Acceptance criteria
- [ ] Statistics view renders
- [ ] Hardcoded data
- [ ] Readable layout
""",
        ),
        (
            "MVP.8: Apply Dashboard Theme and Layout",
            """Apply consistent theme and layout

**Estimation:** 1 day
**Tags:** backend, dashboard, frontend, mvp, priority-medium

### Scope
- Consistent colors, typography
- Sidebar navigation
- Responsive layout

### Acceptance criteria
- [ ] Theme applied across dashboard
- [ ] Sidebar with all sections
- [ ] Basic responsive behavior
""",
        ),
    ]

    print("📋 Creating cards in Newco/Tipio...\n")

    for name, desc in doing_cards:
        card = create_card(DOING_LIST_ID, name, desc, doing_labels)
        print(f"  ✅ Doing: {name[:50]}...")

    print()
    for name, desc in todos_cards:
        card = create_card(TODOS_LIST_ID, name, desc, todos_labels)
        print(f"  ✅ Todos: {name[:50]}...")

    print(f"\n✅ Done. Created {len(doing_cards)} cards in Doing, {len(todos_cards)} cards in Todos.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create Trello cards (in English) documenting Vio Swift SDK work completed.
Follows Dev board card style: ## headers, **Estimation:**, **Tags:**, ### sections.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

DEV_BOARD_ID = "6964ea21570279f07def7786"
TODO_LIST_NAME = "To do"

# Cards following Dev board style: ## headers, **Estimation:**, **Tags:**, ### sections
VIO_SWIFT_CARDS = [
    (
        "[Swift] Reachu → Vio Rebrand: Configuration and Core Types",
        """## Reachu → Vio Rebrand: Configuration and Core

**Estimation:** Completed
**Tags:** Swift, SDK, Rebrand, Config

### Summary
Renamed ReachuConfiguration to VioConfiguration and ReachuCore to VioCore across the Swift SDK.

### Changes completed
- ReachuConfiguration → VioConfiguration
- ReachuCore → VioCore (or ColorScheme when in same module)
- ConfigurationLoader, VioColors, CartModule: ReachuCore type references updated

### Files affected
- ConfigurationLoader.swift
- VioColors.swift
- CartModule.swift
""",
        ["Swift", "SDK", "Rebrand", "Config"],
    ),
    (
        "Reachu → Vio Rebrand: Design System Tokens",
        """## Reachu → Vio Rebrand: Design System

**Estimation:** Completed
**Tags:** Swift, SDK, Rebrand, Config

### Summary
Renamed all design tokens from Reachu prefix to Vio prefix.

### Changes completed
- ReachuColors → VioColors
- ReachuShadow → VioShadow
- ReachuBorderRadius → VioBorderRadius
- ReachuTypography → VioTypography
- ReachuSpacing → VioSpacing

### Files affected
- VioDesignSystem module
- All components using design tokens
""",
        ["Swift", "SDK", "Rebrand", "Config"],
    ),
    (
        "Reachu → Vio Rebrand: UI and Engagement Modules",
        """## Reachu → Vio Rebrand: UI and Engagement

**Estimation:** Completed
**Tags:** Swift, SDK, Rebrand

### Summary
Renamed ReachuUI, ReachuEngagementUI, ReachuEngagementSystem and related files to Vio*.

### Changes completed
- Reachu*.swift files → Vio*.swift
- Module names updated
- All internal references updated

### Files affected
- VioUI, VioEngagementUI, VioEngagementSystem modules
""",
        ["Swift", "SDK", "Rebrand"],
    ),
    (
        "[Swift] Viaplay Demo: Package Reference and Type Fixes",
        """## Viaplay Demo Fixes

**Estimation:** Completed
**Tags:** Swift, SDK, Demo

### Summary
Fixed Viaplay demo to use local ReachuSwiftSDK and resolved ReachuCore type errors.

### Changes completed
- Package reference: `../../../VioSwiftSDK` → `../..` (local ReachuSwiftSDK)
- ReachuCore type errors → VioCore or ColorScheme
- CastingProductCardWrapper: REngagementProductGridCard, REngagementProductData in scope

### Files affected
- Viaplay.xcodeproj/project.pbxproj
- ConfigurationLoader.swift, VioColors.swift, CartModule.swift
""",
        ["Swift", "SDK", "Demo"],
    ),
    (
        "New Vio Documentation Project",
        """## New Vio Documentation Project

**Estimation:** In progress
**Tags:** Documentation, Vio, SDK

### Summary
New documentation project for Vio SDK (Reachu-documentation-v2 / vio-docs).

### Scope
- Documentation site for Vio SDK
- Migration guides Reachu → Vio
- API reference
- Integration examples

### Acceptance criteria
- [ ] Documentation project structure
- [ ] Migration guide Reachu → Vio
- [ ] Swift and Kotlin SDK docs
""",
        ["Documentation", "Vio", "SDK"],
    ),
    (
        "Update Vio Documentation (URLs, References)",
        """## Update Vio Documentation

**Estimation:** 1-2 hours
**Tags:** Documentation, Vio, Rebrand

### Summary
Update existing documentation to replace Reachu references with Vio and update URLs to vio.live.

### Changes required
- docs/README.md: reachu.io → vio.live
- successUrl, cancelUrl, baseUrl GraphQL
- href checkout URLs
- Code examples with new class names (VioConfiguration, VioColors, etc.)

### Acceptance criteria
- [ ] No reachu.io references in docs
- [ ] All URLs point to vio.live
- [ ] Examples use Vio* class names
""",
        ["Documentation", "Vio", "Rebrand"],
    ),
    (
        "Kotlin SDK Parity: Reach Vio Swift State",
        """## Kotlin SDK Parity with Swift

**Estimation:** 8-10 days
**Tags:** Kotlin, SDK, Rebrand

### Summary
Kotlin SDK needs to reach parity with Swift SDK rebrand. See related cards in To do for detailed tasks.

### Tasks (9 cards created)
1. Rename ReachuConfiguration → VioConfiguration
2. Rename design tokens (ReachuColors, etc. → Vio*)
3. Rename ReachuCore → VioCore
4. Rename ReachuUI and components
5. Rename ReachuEngagementUI and ReachuEngagementSystem
6. Update URLs to vio.live
7. Update network_security_config and DynamicComponentsService
8. Update build.gradle and placeholders (email)
9. Add and update Kotlin SDK documentation

### Reference
Swift SDK has all these changes completed. Use as guide.
""",
        ["Kotlin", "SDK", "Rebrand"],
    ),
]


def get_board_lists(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/lists",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def get_board_labels(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/labels",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def find_or_create_label(board_id: str, label_name: str, color: str = "blue"):
    labels = get_board_labels(board_id)
    for label in labels:
        if label.get("name", "").lower() == label_name.lower():
            return label["id"]
    with httpx.Client() as client:
        r = client.post(
            f"{TRELLO_API_BASE}/boards/{board_id}/labels",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "name": label_name,
                "color": color,
            },
        )
        r.raise_for_status()
        return r.json()["id"]


def create_card(list_id: str, name: str, description: str, label_ids: list):
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": name,
        "desc": description,
    }
    if label_ids:
        params["idLabels"] = ",".join(label_ids)

    with httpx.Client() as client:
        r = client.post(f"{TRELLO_API_BASE}/cards", params=params)
        r.raise_for_status()
        return r.json()


def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("Error: TRELLO_API_KEY and TRELLO_TOKEN required in .env")
        sys.exit(1)

    board_id = DEV_BOARD_ID
    print(f"Board Dev (ID: {board_id})")

    lists = get_board_lists(board_id)
    list_obj = next((l for l in lists if l["name"] == TODO_LIST_NAME), None)
    if not list_obj:
        print(f"List '{TODO_LIST_NAME}' not found. Lists: {[l['name'] for l in lists]}")
        sys.exit(1)

    list_id = list_obj["id"]
    print(f"List: {TODO_LIST_NAME}\n")

    all_tags = set()
    for _, _, tags in VIO_SWIFT_CARDS:
        all_tags.update(tags)

    label_cache = {}
    for tag in all_tags:
        label_cache[tag] = find_or_create_label(board_id, tag)

    success = 0
    for title, desc, tags in VIO_SWIFT_CARDS:
        print(f"Creating: {title[:55]}...", end=" ")
        label_ids = [label_cache[t] for t in tags if t in label_cache]
        try:
            card = create_card(list_id, title, desc, label_ids)
            print(f"OK {card['shortUrl']}")
            success += 1
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.5)

    print(f"\nCreated {success}/{len(VIO_SWIFT_CARDS)} cards")


if __name__ == "__main__":
    main()

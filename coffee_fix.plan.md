# Fix Coffee Machine Section Structure

## Problem

Coffee Machine section uses `item_schema` structure which is incompatible with the `renderDynamicList` function. It needs to use the same `fields` structure as the Credit section.

## Solution

Convert Coffee Machine from `item_schema` to `fields` structure, matching the Credit section pattern.

## Implementation

### Update `accounts/rawad_form_schema.py`

**Current structure (BROKEN)**:
```python
{
    "title": "Coffee Machine",
    "type": "dynamic_list",
    "item_schema": [
        {
            "key": "current_amount",
            "label": "Current Amount",
            "type": "number",
            "required": False
        },
        # ... more fields
    ]
}
```

**New structure (FIXED)**:
```python
{
    "title": "Coffee Machine",
    "type": "dynamic_list",
    "fields": [
        {
            "key": "coffee_machine",
            "label": "Coffee Machine Entries",
            "type": "dynamic_list",
            "list_fields": [
                {"key": "current_amount", "label": "Current Amount", "type": "number"},
                {"key": "daily_add", "label": "Daily Add", "type": "number"},
                {"key": "tag", "label": "Tag", "type": "select", "options": [
                    "Paper Cup Small",
                    "Paper Cup Big",
                    "Plastic Cup Small",
                    "Cover Cup Big",
                    "Cover Cup Small",
                    "Small Sticks",
                    "Big Sticks",
                    "Nescafe Shalimon",
                    "Coffee Kg.",
                    "Nescafe Kg.",
                    "Coffee Mate Kg.",
                    "Cadbury Pouder Kg.",
                    "Sugar kg.",
                    "Tea Bags.",
                    "Nestle kg.",
                    "Galon 10L.",
                    "Zanjabil w 3asal",
                    "Gaz 12.5 kg.",
                    "Gaz 10 kg."
                ]}
            ]
        },
        {
            "key": "coffee_machine_total",
            "label": "Coffee Machine Total",
            "type": "number",
            "required": False,
            "readonly": True,
            "calculated": True
        }
    ]
}
```

## Files to Modify

1. **`accounts/rawad_form_schema.py`**:
   - Replace Coffee Machine section with new `fields` structure

## Expected Result

- Coffee Machine section will render correctly like Credit section
- Will have proper "Add Entry" button
- Will display Current Amount, Daily Add, and Tag fields
- Will show a Total field (even if not calculated)
- No JavaScript errors


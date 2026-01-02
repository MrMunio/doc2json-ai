# Schema Creation Guide for Doc2Json AI

This guide explains how to create JSON schemas compatible with the **Doc2Json AI** application. Because this application uses OpenAI's **Structured Outputs (Strict Mode)**, there are specific rules you must follow to ensure your schema works correctly.

## 🚨 The Golden Rule: No Dynamic Keys

**The most important rule:** You cannot use arbitrary/dynamic keys in your objects.

In standard JSON schemas, you might define a "dictionary" where keys are unknown strings (e.g., drug names) and values are their properties.
**This is NOT allowed in Strict Mode.**

### ❌ BAD (Dynamic Keys - Will Fail)
This structure attempts to use unknown strings as keys:
```json
"part_d_tier_structure": { 
    "type": "object", 
    "additionalProperties": { "type": "string" },
    "description": "Drug tier structure where key is Tier Name and value is Cost" 
}
```
*Why it fails:* OpenAI's Strict Mode requires `additionalProperties: false` on all objects. It demands to know every possible key name in advance.

### ✅ GOOD (Array of Objects - Will Work)
Instead, represent dynamic collections as an **Array of Named Objects**:
```json
"part_d_tier_structure": { 
    "type": "array", 
    "items": {
        "type": "object",
        "properties": {
            "tier_name": { "type": "string", "description": "Name of the tier (e.g., Tier 1)" },
            "cost_sharing": { "type": "string", "description": "Cost sharing amount (e.g., $10 copay)" }
        },
        "additionalProperties": false,
        "required": ["tier_name", "cost_sharing"]
    },
    "description": "List of drug tiers and their associated costs" 
}
```

---

## 🛠️ Step-by-Step Schema Construction

Follow these steps to build your `custom_model.schema.json`.

### 1. Root Structure
Your schema file must start with this standard boilerplate. 
*   `type` must be `"object"`.
*   `additionalProperties` must be `false`.
*   `required` must list **all** top-level properties.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MyCustomExtractionModel",
  "type": "object",
  "additionalProperties": false,
  "properties": {
      // Your fields go here
  },
  "required": [
      // List all your property names here
  ]
}
```

### 2. Defining Basic Fields
Always include a `description`. This tells the AI *what* to look for.

*   **Strings** (Text, dates, mixed content)
    ```json
    "provider_name": { 
        "type": "string", 
        "description": "Full legal name of the healthcare provider" 
    }
    ```

*   **Booleans** (Yes/No flags)
    ```json
    "is_in_network": { 
        "type": "boolean", 
        "description": "True if provider is in-network, else false" 
    }
    ```

*   **Numbers/Integers**
    ```json
    "contract_term_years": { 
        "type": "integer", 
        "description": "Duration of the contract in years" 
    }
    ```

### 3. Nested Objects
Group related fields. Remember: `additionalProperties: false` and `required` list are mandatory for **every** object.

```json
"contact_info": {
    "type": "object",
    "properties": {
        "email": { "type": "string", "description": "Primary email address" },
        "phone": { "type": "string", "description": "Office phone number" }
    },
    "additionalProperties": false,
    "required": ["email", "phone"]
}
```

### 4. Arrays (Lists)
Use arrays for lists of items, rules, or exceptions.

```json
"covered_services_list": {
    "type": "array",
    "items": {
        "type": "string"
    },
    "description": "List of all medical services covered by this plan"
}
```

---

## 💡 Best Practices

1.  **Descriptive Key Names**: Use `snake_case` keys that clearly describe the data (e.g., `prior_auth_requirements` instead of `auth`).
2.  **Rich Descriptions**: The `description` field is your "prompt" to the AI. Be specific.
    *   *Weak*: "Date of service"
    *   *Strong*: "The specific date when the medical service was rendered, in YYYY-MM-DD format."
3.  **Handling "Optional" Data**: 
    *   Even if data might be missing, Strict Mode requires the field to be in the schema's `required` list.
    *   The AI will return `null` (if allowed) or an empty string/list if it can't find the data.
    *   To allow nulls: `"type": ["string", "null"]`.

## 🔍 Validation Checklist

Before using your schema, check:
- [ ] Is `additionalProperties: false` set (or implied false/forbid) on all objects?
- [ ] Are dynamic keys (dictionaries) replaced with Arrays of Objects?
- [ ] Do all properties have clear `description` fields?
- [ ] Is the JSON structure valid (no missing commas or braces)?

---

## ⚡ Quick Example: Converting a Legacy Schema

**Legacy (Incompatible):**
```json
"metadata": {
    "type": "object",
    "properties": {
        "tags": { 
            "type": "object",
            "additionalProperties": { "type": "string" } 
        }
    }
}
```

**Modern (Compatible):**
```json
"metadata": {
    "type": "object",
    "properties": {
        "tags": { 
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tag_name": { "type": "string", "description": "Name of the tag" },
                    "tag_value": { "type": "string", "description": "Value of the tag" }
                },
                "additionalProperties": false,
                "required": ["tag_name", "tag_value"]
            },
            "description": "List of metadata tags associated with the document"
        }
    },
    "additionalProperties": false,
    "required": ["tags"]
}
```

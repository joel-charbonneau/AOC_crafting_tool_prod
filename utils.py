def build_hierarchy(item_name, items_data):
    """Build a hierarchy of the item's crafting requirements."""
    # Find the item in the dataset by its itemName
    item = next((i for i in items_data if i["itemName"] == item_name), None)
    if not item:
        return {"name": item_name, "source": ["unknown"], "children": []}

    # Identify sources using the updated identify_sources function
    sources = identify_sources(item)

    # Recursively build the hierarchy for crafted items
    children = []
    if "crafted" in sources:
        for recipe in item.get("_craftingRecipes", []):
            for ingredient in recipe.get("generalResourceCost", []):  # Safely get ingredient list
                ingredient_item = ingredient.get("_item", {})
                ingredient_name = ingredient_item.get("itemName", "")
                if ingredient_name:
                    ingredient_quantity = ingredient.get("quantity", 1)  # Default to 1 if quantity is missing
                    sub_hierarchy = build_hierarchy(ingredient_name, items_data)
                    sub_hierarchy["quantity"] = ingredient_quantity
                    children.append(sub_hierarchy)

    return {
        "name": item["itemName"],
        "source": sources,
        "children": children,
    }

def calculate_total_requirements(hierarchy, totals=None, multiplier=1):
    """
    Calculate the total quantities of bottom-level items required for a recipe,
    returning results in the same format as sum_non_crafted_items.
    """
    if totals is None:
        totals = {}

    # Current item's quantity after applying the multiplier
    current_quantity = hierarchy.get("quantity", 1) * multiplier

    # If the item is non-crafted, add its quantity to the totals
    if "crafted" not in hierarchy.get("source", []):
        item_name = hierarchy["name"]
        if item_name not in totals:
            totals[item_name] = {
                "name": item_name,
                "quantity": 0,
                "source": hierarchy.get("source", []),
            }
        totals[item_name]["quantity"] += current_quantity

    # Recursively process children with the updated multiplier
    for child in hierarchy.get("children", []):
        calculate_total_requirements(child, totals, current_quantity)

    # Convert the totals dictionary to a list of dictionaries for consistency
    return list(totals.values())


def identify_sources(item):
    """Identify all applicable sources for an item."""
    sources = []
    
    if "_craftingRecipes" in item and item["_craftingRecipes"]:
        sources.append("crafted")
    if "_droppedBy" in item and item["_droppedBy"]:
        sources.append("drop")
    if "_soldBy" in item and item["_soldBy"]:
        sources.append("vendor")
    if item.get("gameplayTags", {}).get("parentTags", []):
        parent_tags = [tag["tagName"] for tag in item["gameplayTags"]["parentTags"]]
        if "Artisanship.Gathering" in parent_tags and "Item.Resource.Raw" in parent_tags:
            sources.append("gathered")
    
    return sources if sources else ["unknown"]

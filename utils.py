def build_hierarchy(item_name, items_data, visited=None):
    """
    Build the crafting hierarchy for a given item.
    Detect and handle cyclic dependencies.
    """
    # Initialize the visited set on the first call
    if visited is None:
        visited = set()

    # Find the item in the dataset by its itemName
    item = next((i for i in items_data if i["itemName"] == item_name), None)
    if not item:
        return None  # Skip items not found in the dataset

    # Detect cyclic dependency
    if item_name in visited:
        return None  # Skip cyclic dependencies

    # Mark the item as visited
    visited.add(item_name)

    # Determine the source(s) of the item
    sources = identify_sources(item)

    # Recursively build the hierarchy for crafted items
    children = []
    if "_craftingRecipes" in item:
        for recipe in item["_craftingRecipes"]:
            for cost_key in ["primaryResourceCosts", "generalResourceCost"]:
                for ingredient in recipe.get(cost_key, []):
                    ingredient_item = ingredient.get("_item", {})
                    ingredient_name = ingredient_item.get("itemName", "")
                    if ingredient_name:
                        ingredient_quantity = ingredient.get("quantity", 1)
                        sub_hierarchy = build_hierarchy(ingredient_name, items_data, visited)
                        if sub_hierarchy:  # Add only non-None sub-hierarchies
                            sub_hierarchy["quantity"] = ingredient_quantity
                            children.append(sub_hierarchy)

    # Remove the item from visited before returning
    visited.remove(item_name)

    # Return the hierarchy only if it has meaningful data
    return {
        "name": item["itemName"],
        "source": sources,
        "children": children,
    } if children or sources else None

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
    if any(tag in hierarchy.get("source", []) for tag in ["drop", "vendor"]):
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

    def get_cert_and_profession(item):
        """Extract formatted certification and profession without 'None' values."""
        certification_tag = item.get("certificationTag", {}).get("tagName", "")
        profession_tag = item.get("professionTag", {}).get("tagName", "")

        if certification_tag and profession_tag:  # Ensure both are valid
            cert_level = certification_tag.split(".")[-1]  # Extract last part of certification
            profession = profession_tag.split(".")[-1]  # Extract last part of profession
            return f"{cert_level} {profession}"
        return None

    # Check for crafted items
    if "_craftingRecipes" in item and item["_craftingRecipes"]:
        cert_and_prof = get_cert_and_profession(item)
        if cert_and_prof:
            sources.append(cert_and_prof)
        else:
            sources.append("crafted")

    # Check for drop sources
    if "_droppedBy" in item and item["_droppedBy"]:
        sources.append("drop")

    # Check for vendor sources
    if "_soldBy" in item and item["_soldBy"]:
        sources.append("vendor")

    # Check for gathered items
    parent_tags = item.get("gameplayTags", {}).get("parentTags", [])
    if any(tag.get("tagName") == "Artisanship.Gathering" for tag in parent_tags):
        cert_and_prof = get_cert_and_profession(item)
        if cert_and_prof:
            sources.append(cert_and_prof)
        else:
            sources.append("gathered")

    return sources if sources else ["unknown"]

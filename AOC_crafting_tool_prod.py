from flask import Flask, request, render_template, jsonify
import json, requests
from utils import build_hierarchy, calculate_total_requirements, identify_sources

def fetch_all_items_json():
    url = "https://github.com/joel-charbonneau/AOC_crafting_tool_prod/raw/refs/heads/main/all_items.json"  # Replace with your Raw URL
    try:
        response = requests.get(url, timeout=10)  # Added timeout for reliability
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all_items.json: {e}")
        return []  # Return an empty list as a fallback

# Use the function to load the items
all_items = fetch_all_items_json()
if not all_items:
    print("Warning: No items loaded. The application may have limited functionality.")

# Example: Print the number of items loaded
if all_items:
    print(f"Successfully loaded {len(all_items)} items.")
else:
    print("No items loaded.")

# Initialize Flask app
app = Flask(__name__)

# Routes
@app.route("/")
def index():
    """Homepage with item selection form."""
    craftable_items = sorted([item["itemName"] for item in all_items if "_craftingRecipes" in item and item["_craftingRecipes"]])
    return render_template("index.html", items=craftable_items)

@app.route("/get_hierarchy", methods=["POST"])
def get_hierarchy():
    """Process item selection and return hierarchy."""
    item_name = request.form.get("item_name")
    if not item_name:
        return jsonify({"error": "No item name provided"}), 400
    hierarchy = build_hierarchy(item_name, all_items)
    non_crafted_totals = calculate_total_requirements(hierarchy)
    return jsonify({"hierarchy": hierarchy, "non_crafted_totals": non_crafted_totals})

# Run the app
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

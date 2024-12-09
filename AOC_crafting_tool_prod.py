from flask import Flask, request, render_template, jsonify
import json, requests
from utils import build_hierarchy, calculate_total_requirements, identify_sources

def fetch_all_items_json():
    url = "https://github.com/joel-charbonneau/AOC_crafting_tool_prod/raw/refs/heads/main/all_items.json"  # Replace with your Raw URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all_items.json: {e}")
        return None

# Use the function to load the items
all_items = fetch_all_items_json()
if all_items is None:
    raise RuntimeError("Failed to load all_items.json from external source")

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
    item_names = sorted([item["itemName"] for item in all_items])  # All item names sorted alphabetically
    return render_template("index.html", items=item_names)

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
    app.run(debug=True)

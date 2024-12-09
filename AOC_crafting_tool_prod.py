from flask import Flask, request, render_template, jsonify
import json, gdown, requests, os
from utils import build_hierarchy, calculate_total_requirements, identify_sources

# Define the path to your JSON file
file_path = "all_items.json"

# Load the JSON data
def load_all_items(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}.")
        return []

# Use the function to load the items
all_items = load_all_items(file_path)

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

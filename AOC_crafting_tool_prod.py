from flask import Flask, request, render_template, jsonify
import json, gdown, requests
from utils import build_hierarchy, calculate_total_requirements, identify_sources

def load_all_items(file_path="all_items.json"):
    """Load the all_items.json file into memory."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist. Ensure it is downloaded via GitHub LFS.")
    
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Example usage
try:
    all_items = load_all_items()
    print("Loaded all_items.json successfully!")
except FileNotFoundError as e:
    print(str(e))

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

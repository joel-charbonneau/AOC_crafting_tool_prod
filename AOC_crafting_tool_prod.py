from flask import Flask, request, render_template, jsonify
import json, gdown, os
from utils import build_hierarchy, calculate_total_requirements, identify_sources

# Load data
def load_items_from_google_drive():
    # Google Drive file ID
    file_id = "1q2pYd9En9V3hlDgEUhCyr51Tyv89cJnh"
    file_path = "all_items.json"

    # Check if the file already exists locally
    if not os.path.exists(file_path):
        # Construct the download URL
        url = f"https://drive.google.com/uc?id={file_id}"
        print("Downloading all_items.json from Google Drive...")
        gdown.download(url, file_path, quiet=False)

    # Load the JSON file
    with open(file_path, "r") as f:
        return json.load(f)

# Load items
all_items = load_items_from_google_drive()

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

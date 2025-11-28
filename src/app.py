import os
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# In-memory storage for warehouses (dict of id -> {name, varasto})
warehouses = {}
next_id = 1


def get_next_id():
    """Get the next available warehouse ID."""
    global next_id
    current_id = next_id
    next_id += 1
    return current_id


def reset_app_state():
    """Reset the application state for testing purposes."""
    global next_id
    warehouses.clear()
    next_id = 1


@app.route("/")
def index():
    """Display all warehouses."""
    return render_template("index.html", warehouses=warehouses)


@app.route("/warehouse/new", methods=["GET", "POST"])
def create_warehouse():
    """Create a new warehouse."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            tilavuus = float(request.form.get("tilavuus", 0))
        except ValueError:
            flash("Invalid capacity value.", "error")
            return render_template("create_warehouse.html")

        try:
            alku_saldo = float(request.form.get("alku_saldo", 0))
        except ValueError:
            flash("Invalid initial balance value.", "error")
            return render_template("create_warehouse.html")

        if not name:
            flash("Warehouse name is required.", "error")
            return render_template("create_warehouse.html")

        if tilavuus <= 0:
            flash("Capacity must be greater than 0.", "error")
            return render_template("create_warehouse.html")

        warehouse_id = get_next_id()
        warehouses[warehouse_id] = {
            "name": name,
            "varasto": Varasto(tilavuus, alku_saldo)
        }
        flash(f"Warehouse '{name}' created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("create_warehouse.html")


@app.route("/warehouse/<int:warehouse_id>")
def view_warehouse(warehouse_id):
    """View a specific warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        flash("Warehouse not found.", "error")
        return redirect(url_for("index"))
    return render_template("view_warehouse.html",
                           warehouse_id=warehouse_id,
                           warehouse=warehouse)


@app.route("/warehouse/<int:warehouse_id>/add", methods=["POST"])
def add_to_warehouse(warehouse_id):
    """Add content to a warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        flash("Warehouse not found.", "error")
        return redirect(url_for("index"))

    try:
        maara = float(request.form.get("maara", 0))
    except ValueError:
        flash("Invalid amount value.", "error")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    if maara <= 0:
        flash("Amount must be greater than 0.", "error")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    available_space = warehouse["varasto"].paljonko_mahtuu()
    if available_space <= 0:
        flash("Warehouse is full. Cannot add more content.", "error")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    warehouse["varasto"].lisaa_varastoon(maara)
    flash(f"Added {maara} units to warehouse.", "success")
    return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))


@app.route("/warehouse/<int:warehouse_id>/remove", methods=["POST"])
def remove_from_warehouse(warehouse_id):
    """Remove content from a warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        flash("Warehouse not found.", "error")
        return redirect(url_for("index"))

    try:
        maara = float(request.form.get("maara", 0))
    except ValueError:
        flash("Invalid amount value.", "error")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    if maara <= 0:
        flash("Amount must be greater than 0.", "error")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    removed = warehouse["varasto"].ota_varastosta(maara)
    flash(f"Removed {removed} units from warehouse.", "success")
    return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))


@app.route("/warehouse/<int:warehouse_id>/edit", methods=["GET", "POST"])
def edit_warehouse(warehouse_id):
    """Edit a warehouse's name."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        flash("Warehouse not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Warehouse name is required.", "error")
            return render_template("edit_warehouse.html",
                                   warehouse_id=warehouse_id,
                                   warehouse=warehouse)

        warehouse["name"] = name
        flash(f"Warehouse renamed to '{name}'.", "success")
        return redirect(url_for("view_warehouse", warehouse_id=warehouse_id))

    return render_template("edit_warehouse.html",
                           warehouse_id=warehouse_id,
                           warehouse=warehouse)


@app.route("/warehouse/<int:warehouse_id>/delete", methods=["POST"])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    warehouse = warehouses.get(warehouse_id)
    if not warehouse:
        flash("Warehouse not found.", "error")
        return redirect(url_for("index"))

    name = warehouse["name"]
    del warehouses[warehouse_id]
    flash(f"Warehouse '{name}' deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5000)

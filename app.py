
import os
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.database import get_db, init_db

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
# Initialize database
init_db()


def allowed_file(filename):
    
    return (
        "." in filename and
        filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    db = get_db()

    featured_items = db.execute("""

        SELECT *

        FROM marketplace_items

        ORDER BY created_at DESC

        LIMIT 4

    """).fetchall()

    featured_campaigns = db.execute("""

        SELECT *

        FROM campaigns

        ORDER BY id DESC

        LIMIT 3

    """).fetchall()

    db.close()

    return render_template(

        "index.html",

        featured_items=featured_items,

        featured_campaigns=featured_campaigns

    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/campaigns")
def campaigns():

    campaigns = [

        {
            "id": 1,
            "title": "School Supplies For Rural Students",
            "category": "Education",
            "description": "Help provide school bags, notebooks, uniforms and essential learning materials.",
            "goal": 50000,
            "raised": 36000,
            "supporters": 820,
            "days_left": 14,
            "image": "images/campaigns/campaign1.jpg"
        },

        {
            "id": 2,
            "title": "Food Donation Drive",
            "category": "Food",
            "description": "Support families by contributing essential food supplies.",
            "goal": 50000,
            "raised": 34000,
            "supporters": 620,
            "days_left": 18,
            "image": "images/campaigns/campaign2.jpg"
        },

        {
            "id": 3,
            "title": "Student Essentials",
            "category": "Essentials",
            "description": "Donate furniture, laptops, books and stationery.",
            "goal": 50000,
            "raised": 30000,
            "supporters": 500,
            "days_left": 20,
            "image": "images/campaigns/campaign3.jpg"
        }

    ]

    stats = {
        "campaigns": len(campaigns),
        "raised": sum(c["raised"] for c in campaigns),
        "supporters": sum(c["supporters"] for c in campaigns),
        "success": "100%"
    }

    featured = campaigns[0]

    return render_template(
        "campaigns.html",
        campaigns=campaigns,
        featured=featured,
        stats=stats
    )
@app.route("/campaign/<int:campaign_id>")
def campaign_details(campaign_id):

    campaigns = {

        1: {
            "id": 1,
            "title": "School Supplies For Rural Students",
            "category": "Education",
            "description": "Help provide school bags, notebooks, uniforms and essential learning materials.",
            "story": "Every child deserves access to quality education. This campaign provides books, notebooks, school bags and learning materials to students in rural areas.",
            "goal": 50000,
            "raised": 36000,
            "supporters": 820,
            "days_left": 14,
            "image": "images/campaigns/campaign1.jpg"
        },

        2: {
            "id": 2,
            "title": "Food Donation Drive",
            "category": "Food",
            "description": "Support families by contributing essential food supplies.",
            "story": "Providing nutritious food kits to underprivileged families.",
            "goal": 50000,
            "raised": 34000,
            "supporters": 620,
            "days_left": 18,
            "image": "images/campaigns/campaign2.jpg"
        },

        3: {
            "id": 3,
            "title": "Student Essentials",
            "category": "Essentials",
            "description": "Donate furniture, laptops, books and stationery.",
            "story": "Helping students get access to the essential items they need for education.",
            "goal": 50000,
            "raised": 30000,
            "supporters": 500,
            "days_left": 20,
            "image": "images/campaigns/campaign3.jpg"
        }

    }

    campaign = campaigns.get(campaign_id)

    if campaign is None:
        return render_template("404.html"), 404

    return render_template(
        "campaign_details.html",
        campaign=campaign
    )

@app.route("/donate/<int:campaign_id>", methods=["GET", "POST"])
def donate_campaign(campaign_id):
    db = get_db()

    campaign = db.execute(
        """
        SELECT *
        FROM campaigns
        WHERE id = ?
        """,
        (campaign_id,)
    ).fetchone()

    print("Campaign ID requested:", campaign_id)
    print("Campaign found:", campaign)

    all_campaigns = db.execute("SELECT id, title FROM campaigns").fetchall()
    print("All campaigns:", [dict(c) for c in all_campaigns])

    if campaign is None:
        db.close()
        return render_template("404.html"), 404

    if request.method == "POST":
        amount = request.form.get("custom_amount")

        if not amount:
            amount = request.form.get("amount")

        amount = float(amount)

        db.execute(
            """
            INSERT INTO donations
            (
                campaign_id,
                donor_name,
                donor_email,
                phone,
                amount,
                payment_method,
                message
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                campaign_id,
                request.form["name"],
                request.form["email"],
                request.form["phone"],
                amount,
                request.form["payment"],
                request.form.get("message", "")
            )
        )

        db.execute(
            """
            UPDATE campaigns
            SET
                raised = raised + ?,
                supporters = supporters + 1
            WHERE id = ?
            """,
            (
                amount,
                campaign_id
            )
        )

        db.commit()
        db.close()

        flash("Thank you for your donation!", "success")

        return redirect(
            url_for(
                "thank_you",
                campaign_id=campaign_id,
                amount=amount
            )
        )

    db.close()
    return render_template(
        "donate.html",
        campaign=campaign
    )

from datetime import datetime

@app.route("/thank-you/<int:campaign_id>")
def thank_you(campaign_id):

    amount = request.args.get("amount")

    transaction_id = "KK" + datetime.now().strftime("%Y%m%d%H%M%S")

    return render_template(
        "thank_you.html",
        amount=amount,
        campaign_id=campaign_id,
        transaction_id=transaction_id
    )
    
@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/item/<int:item_id>")
def item_details(item_id):

    db = get_db()

    item = db.execute("""
        SELECT
            marketplace_items.*,
            users.full_name
        FROM marketplace_items
        JOIN users
            ON marketplace_items.seller_id = users.id
        WHERE marketplace_items.id = ?
    """, (item_id,)).fetchone()

    db.close()

    if item is None:
        return render_template("404.html"), 404

    return render_template(
        "item_details.html",
        item=item
    )
# =====================================================
# MARKETPLACE
# =====================================================

@app.route("/marketplace")
def marketplace():

    db = get_db()

    items = db.execute("""
        SELECT
            marketplace_items.*,
            users.full_name
        FROM marketplace_items
        JOIN users
            ON marketplace_items.seller_id = users.id
        WHERE marketplace_items.status = 'available'
        ORDER BY marketplace_items.created_at DESC
    """).fetchall()

    db.close()

    return render_template(
        "marketplace.html",
        items=items
    )


@app.route("/sell-item", methods=["GET", "POST"])
def sell_item():

    if "user_id" not in session:

        flash("Please login first.","warning")

        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]

        description = request.form["description"]

        category = request.form["category"]

        condition = request.form["condition"]

        price = request.form["price"]

        image_name = None

        image = request.files.get("image")

        if image and image.filename != "":

            if allowed_file(image.filename):

                filename = secure_filename(image.filename)
               
                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                image_name = filename

        db = get_db()

        db.execute("""

        INSERT INTO marketplace_items
        (
            seller_id,
            title,
            description,
            category,
            price,
            condition,
            image
        )

        VALUES
        (?,?,?,?,?,?,?)

        """,

        (

            session["user_id"],

            title,

            description,

            category,

            price,

            condition,

            image_name

        ))

        db.commit()

        db.close()

        flash(
            "Item listed successfully!",
            "success"
        )

        return redirect(url_for("marketplace"))

    return render_template("sell_item.html")


# =====================================================
# EDIT ITEM
# =====================================================

@app.route("/edit-item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    item = db.execute(
        """
        SELECT *
        FROM marketplace_items
        WHERE id = ?
        """,
        (item_id,)
    ).fetchone()

    if item is None:
        db.close()
        return render_template("404.html"), 404

    # Authorization
    if item["seller_id"] != session["user_id"]:
        db.close()
        flash("You are not authorized to edit this item.", "error")
        return redirect(url_for("my_listings"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        condition = request.form["condition"]
        price = request.form["price"]

        image_name = item["image"]

        image = request.files.get("image")

        if image and image.filename != "":
            if allowed_file(image.filename):

                filename = secure_filename(image.filename)

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                image_name = filename

        db.execute(
            """
            UPDATE marketplace_items

            SET
                title=?,
                description=?,
                category=?,
                condition=?,
                price=?,
                image=?

            WHERE id=?
            """,
            (
                title,
                description,
                category,
                condition,
                price,
                image_name,
                item_id
            )
        )

        db.commit()
        db.close()

        flash("Item updated successfully!", "success")

        return redirect(url_for("my_listings"))

    db.close()

    return render_template(
        "edit_item.html",
        item=item
    )
    
    # =====================================================
# DELETE ITEM
# =====================================================

@app.route("/delete-item/<int:item_id>", methods=["POST"])
def delete_item(item_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    item = db.execute(
        """
        SELECT *
        FROM marketplace_items
        WHERE id = ?
        """,
        (item_id,)
    ).fetchone()

    if item is None:
        db.close()
        return render_template("404.html"), 404

    # Authorization - only owner can delete
    if item["seller_id"] != session["user_id"]:
        db.close()
        flash("You are not authorized to delete this item.", "error")
        return redirect(url_for("my_listings"))

    # Delete the record
    db.execute(
        """
        DELETE FROM marketplace_items
        WHERE id = ?
        """,
        (item_id,)
    )

    db.commit()
    db.close()

    flash("Item deleted successfully!", "success")

    return redirect(url_for("my_listings"))
# =====================================================
# REGISTER
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()

        email = request.form["email"].strip().lower()

        phone = request.form.get("phone", "").strip()

        college = request.form.get("college", "").strip()

        password = request.form["password"]

        db = get_db()

        existing = db.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if existing:

            flash(
                "Email already registered.",
                "error"
            )

            db.close()

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        db.execute("""

        INSERT INTO users
        (
            full_name,
            email,
            password,
            phone,
            college
        )

        VALUES
        (
            ?,?,?,?,?
        )

        """,
        (
            full_name,
            email,
            hashed_password,
            phone,
            college
        ))

        db.commit()

        db.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        db = get_db()

        user = db.execute(

            "SELECT * FROM users WHERE email=?",

            (email,)

        ).fetchone()

        db.close()

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(url_for("login"))

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(url_for("login"))

        session["user_id"] = user["id"]

        session["user_name"] = user["full_name"]

        session["role"] = user["role"]

        flash(
            f"Welcome {user['full_name']}!",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    role = session.get("role", "donor")

    if role == "admin":
        return render_template(
            "admin_dashboard.html",
            name=session["user_name"]
        )

    if role == "ngo":
        return render_template(
            "ngo_dashboard.html",
            name=session["user_name"]
        )

    # -----------------------
    # DONOR DASHBOARD
    # -----------------------

    db = get_db()

    donations = db.execute(
        """
        SELECT
            campaigns.title,
            donations.amount,
            donations.donated_at
        FROM donations
        JOIN campaigns
            ON campaigns.id = donations.campaign_id
        ORDER BY donations.donated_at DESC
        """
    ).fetchall()

    total_amount = db.execute(
        """
        SELECT IFNULL(SUM(amount),0)
        FROM donations
        """
    ).fetchone()[0]

    total_donations = db.execute(
        """
        SELECT COUNT(*)
        FROM donations
        """
    ).fetchone()[0]
    db.close()

    return render_template(
        "donor_dashboard.html",
        name=session["user_name"],
        donations=donations,
        total_amount=total_amount,
        total_donations=total_donations
    )

@app.route("/profile")
def profile():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    db.close()

    return render_template(
        "profile.html",
        user=user
    )
# =====================================================
# MY LISTINGS
# =====================================================

@app.route("/my-listings")
def my_listings():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    items = db.execute("""

        SELECT *

        FROM marketplace_items

        WHERE seller_id = ?

        ORDER BY created_at DESC

    """, (session["user_id"],)).fetchall()

    db.close()

    return render_template(
        "my_listings.html",
        items=items
    )

# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(url_for("home"))


# =====================================================
# ERROR 404
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# =====================================================
# EDIT PROFILE
# =====================================================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]
        college = request.form["college"]

        profile_path = user["profile_image"]

        image = request.files.get("profile_image")

        if image and image.filename != "":

            if allowed_file(image.filename):

                filename = secure_filename(image.filename)

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                profile_path = "uploads/" + filename

        db.execute(
            """
            UPDATE users
            SET
                full_name=?,
                phone=?,
                college=?,
                profile_image=?
            WHERE id=?
            """,
            (
                full_name,
                phone,
                college,
                profile_path,
                session["user_id"]
            )
        )

        db.commit()

        session["user_name"] = full_name

        flash("Profile updated successfully!", "success")

        db.close()

        return redirect(url_for("profile"))

    db.close()

    return render_template(
        "edit_profile.html",
        user=user
    )
# =====================================================
# CHANGE PASSWORD
# =====================================================

from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    if request.method == "POST":

        current = request.form["current_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if not check_password_hash(user["password"], current):
            flash("Current password is incorrect.", "danger")
            db.close()
            return redirect(url_for("change_password"))

        if new != confirm:
            flash("Passwords do not match.", "danger")
            db.close()
            return redirect(url_for("change_password"))

        db.execute(
            """
            UPDATE users
            SET password=?
            WHERE id=?
            """,
            (
                generate_password_hash(new),
                session["user_id"]
            )
        )

        db.commit()
        db.close()

        flash("Password changed successfully.", "success")

        return redirect(url_for("profile"))

    db.close()

    return render_template("change_password.html")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
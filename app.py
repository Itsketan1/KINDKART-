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
            "description": "Provide books, uniforms and stationery to children.",
            "category": "Education",
            "image": "images/campaigns/campaign1.jpg",
            "goal": 50000,
            "raised": 36000,
            "days_left": 14
        },
        {
            "id": 2,
            "title": "Community Food Drive",
            "description": "Provide meals to families facing hardship.",
            "category": "Food",
            "image": "images/campaigns/campaign2.jpg",
            "goal": 30000,
            "raised": 27000,
            "days_left": 6
        }
    ]

    featured = campaigns[0]

    stats = {
        "campaigns": len(campaigns),
        "raised": "$245K",
        "supporters": "820+",
        "success": "96%"
    }

    return render_template(
        "campaigns.html",
        campaigns=campaigns,
        featured=featured,
        stats=stats
    )

@app.route("/campaign/<int:campaign_id>")
def campaign_details(campaign_id):

    campaign = {
    "id": campaign_id,
    "title": "School Supplies For Rural Students",
    "category": "Education",
    "description": "Help provide school bags, notebooks, uniforms and essential learning materials for children studying in rural communities.",
    "story": """
Every child deserves access to quality education.

This campaign aims to provide educational resources to students living in rural villages where families struggle to afford basic school supplies.

With community support we can ensure hundreds of children continue learning with confidence.
""",
    "goal": 50000,
    "raised": 36000,
    "supporters": 820,
    "days_left": 14,
    "image": "images/campaigns/campaign1.jpg"
}
    return render_template(
        "campaign_details.html",
        campaign=campaign
    )


@app.route("/donate/<int:campaign_id>", methods=["GET", "POST"])
def donate_campaign(campaign_id):

    campaign = {
        "id": campaign_id,
        "title": "School Supplies For Rural Students",
        "category": "Education",
        "description": "Providing school supplies for rural students.",
        "goal": 50000,
        "raised": 36000,
        "supporters": 820,
        "days_left": 14,
        "image": "images/campaigns/campaign1.jpg"
    }

    if request.method == "POST":

        donor_name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        amount = request.form.get("amount")
        payment = request.form.get("payment")

        print("Donation Received")
        print(donor_name, email, phone, amount, payment)

        return redirect(url_for(
            "thank_you",
            campaign_id=campaign_id,
            amount=amount
        ))

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

    return render_template(
        "donor_dashboard.html",
        name=session["user_name"]
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
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
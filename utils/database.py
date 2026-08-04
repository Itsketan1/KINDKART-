import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"

# Create database folder if it doesn't exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "kindkart.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    # ===========================
    # USERS
    # ===========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        phone TEXT,

        college TEXT,

        role TEXT DEFAULT 'student',

        profile_image TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ===========================
    # CAMPAIGNS
    # ===========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    category TEXT,

    description TEXT,

    goal REAL,

    raised REAL DEFAULT 0,

    supporters INTEGER DEFAULT 0,

    image TEXT,

    ngo_name TEXT,

    status TEXT DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
    """)

    # ===========================
    # DONATIONS
    # ===========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    campaign_id INTEGER NOT NULL,

    donor_name TEXT NOT NULL,

    donor_email TEXT,

    phone TEXT,

    amount REAL NOT NULL,

    payment_method TEXT,

    message TEXT,

    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(campaign_id)
        REFERENCES campaigns(id)
        ON DELETE CASCADE
    )
    """)

    # ===========================
    # MARKETPLACE ITEMS
    # ===========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketplace_items (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL,
        condition TEXT,
        image TEXT,
        status TEXT DEFAULT 'available',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (seller_id) REFERENCES users(id)

    )
    """)

    # ===========================
    # DATABASE INDEXES
    # ===========================

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_marketplace_status
    ON marketplace_items(status)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_marketplace_seller
    ON marketplace_items(seller_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_campaign_status
    ON campaigns(status)
    """)
    # ===========================
    # DEFAULT CAMPAIGNS
    # ===========================
    cursor.execute("SELECT COUNT(*) FROM campaigns")
    count = cursor.fetchone()[0]

    if count == 0:
        campaigns = [
            (
                "School Supplies For Rural Students",
                "Education",
                "Help provide school bags, notebooks, uniforms and essential learning materials.",
                50000,
                36000,
                820,
                "images/campaigns/campaign1.jpg",
                "KindKart NGO"
            ),
            (
                "Food Donation Drive",
                "Food",
                "Support families by contributing essential food supplies.",
                50000,
                34000,
                620,
                "images/campaigns/campaign2.jpg",
                "KindKart NGO"
            ),
            (
                "Student Essentials",
                "Essentials",
                "Donate furniture, laptops, books and stationery.",
                50000,
                30000,
                500,
                "images/campaigns/campaign3.jpg",
                "KindKart NGO"
            )
        ]
        cursor.executemany(
            """
            INSERT INTO campaigns
            (
                title,
                category,
                description,
                goal,
                raised,
                supporters,
                image,
                ngo_name
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            campaigns
        )
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()
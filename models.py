from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class URL(db.Model):
    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)

    original_url = db.Column(db.String(500), nullable=False)

    short_code = db.Column(db.String(10), unique=True, nullable=False)

    title = db.Column(db.String(200))

    domain = db.Column(db.String(200))

    total_clicks = db.Column(db.Integer, default=0)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    expires_at = db.Column(db.DateTime, nullable=True)

    clicks = db.relationship(
        "Click",
        backref="url",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<URL {self.short_code}>"


class Click(db.Model):
    __tablename__ = "clicks"

    id = db.Column(db.Integer, primary_key=True)

    url_id = db.Column(
        db.Integer,
        db.ForeignKey("urls.id"),
        nullable=False
    )

    clicked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    ip_address = db.Column(db.String(50))

    browser = db.Column(db.String(100))

    browser_version = db.Column(db.String(50))

    operating_system = db.Column(db.String(100))

    device_type = db.Column(db.String(50))

    user_agent = db.Column(db.Text)

    referrer = db.Column(db.String(500))

    country = db.Column(db.String(100))

    city = db.Column(db.String(100))

    def __repr__(self):
        return f"<Click {self.id}>"
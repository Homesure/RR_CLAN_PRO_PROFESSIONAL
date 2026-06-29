from flask_login import UserMixin
from datetime import datetime
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(160), unique=True, nullable=False)

    phone = db.Column(db.String(20), unique=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(30), nullable=False, default="customer")

    skill = db.Column(db.String(80))

    wallet_balance = db.Column(db.Integer, default=0)

    referral_code = db.Column(db.String(40), unique=True, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer_bookings = db.relationship(
        "Booking",
        foreign_keys="Booking.customer_id",
        backref="customer",
        lazy=True,
    )

    assigned_jobs = db.relationship(
        "Booking",
        foreign_keys="Booking.technician_id",
        backref="technician",
        lazy=True,
    )


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    clan = db.Column(db.String(80), nullable=False)

    category = db.Column(
        db.String(100),
        nullable=False,
        default="General"
    )

    name = db.Column(db.String(120), nullable=False)

    price = db.Column(db.Integer, nullable=False)

    duration = db.Column(db.String(80), nullable=False)

    description = db.Column(
        db.Text,
        default="Professional RR CLAN PRO service with verified technician support."
    )

    image = db.Column(
        db.String(255),
        nullable=False,
        default="default.jpg"
    )

    skill_required = db.Column(db.String(80), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service.id"),
        nullable=False
    )

    customer_name = db.Column(db.String(120), nullable=False)

    phone = db.Column(db.String(20), nullable=False)

    address = db.Column(db.Text, nullable=False)

    building_no = db.Column(db.String(120), nullable=True)

    floor = db.Column(db.String(80), nullable=True)

    landmark = db.Column(db.String(160), nullable=True)

    latitude = db.Column(db.String(80), nullable=True)

    longitude = db.Column(db.String(80), nullable=True)

    map_link = db.Column(db.Text, nullable=True)

    booking_date = db.Column(db.String(30), nullable=False)

    booking_time = db.Column(db.String(30), nullable=False)

    notes = db.Column(db.Text)

    status = db.Column(db.String(40), default="Pending")

    payment_status = db.Column(db.String(40), default="Unpaid")

    payment_method = db.Column(
        db.String(50),
        default="Cash After Service"
    )

    razorpay_order_id = db.Column(
        db.String(200),
        nullable=True
    )

    razorpay_payment_id = db.Column(
        db.String(200),
        nullable=True
    )

    razorpay_signature = db.Column(
        db.String(300),
        nullable=True
    )

    invoice_number = db.Column(
        db.String(80),
        nullable=True
    )

    coupon_code = db.Column(
        db.String(100),
        nullable=True
    )

    referral_code_used = db.Column(
        db.String(40),
        nullable=True
    )

    referred_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    referral_reward_given = db.Column(
        db.Boolean,
        default=False
    )

    discount = db.Column(
        db.Integer,
        default=0
    )

    gst_amount = db.Column(
        db.Integer,
        default=0
    )

    total_amount = db.Column(
        db.Integer,
        default=0
    )

    rating = db.Column(db.Integer, nullable=True)

    review = db.Column(db.Text, nullable=True)

    technician_notification = db.Column(
        db.String(255),
        default="No technician assigned yet"
    )

    customer_notification = db.Column(
        db.String(255),
        default="Your booking has been created. Admin will assign a technician soon."
    )

    notification_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship("Service", backref="bookings")

    referred_by = db.relationship(
        "User",
        foreign_keys=[referred_by_user_id],
        backref="referred_bookings"
    )


class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=True
    )

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Open"
    )

    admin_reply = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customer = db.relationship(
        "User",
        backref="support_tickets"
    )

    booking = db.relationship(
        "Booking",
        backref="support_tickets"
    )
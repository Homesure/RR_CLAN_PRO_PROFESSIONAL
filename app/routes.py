from flask import (
    render_template,
    render_template_string,
    redirect,
    url_for,
    flash,
    request,
    make_response,
    current_app,
    session,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from xhtml2pdf import pisa
from io import BytesIO
from app import db
from app.models import User, Partner, Service, Booking, SupportTicket
import random
import razorpay


def generate_referral_code(name):
    clean_name = "".join(name.upper().split())[:4]

    if not clean_name:
        clean_name = "RRCP"

    while True:
        code = f"{clean_name}{random.randint(1000, 9999)}"
        existing = User.query.filter_by(referral_code=code).first()

        if not existing:
            return code


def get_razorpay_client():
    key_id = current_app.config.get("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        return None

    return razorpay.Client(auth=(key_id, key_secret))


def register_routes(app):

    @app.route("/")
    def index():
        services = Service.query.all()
        grouped_services = {}

        for service in services:
            grouped_services.setdefault(service.clan, []).append(service)

        return render_template("index.html", grouped_services=grouped_services)

    @app.route("/services")
    def services():
        services = Service.query.all()
        service_data = {}

        for service in services:
            service_data.setdefault(service.clan, {})
            service_data[service.clan].setdefault(service.category, [])
            service_data[service.clan][service.category].append(service)

        return render_template("services.html", service_data=service_data)


    # ---------------- PARTNER PORTAL ----------------

    @app.route("/partner/register", methods=["GET", "POST"])
    def partner_register():
        if request.method == "POST":
            business_name = (request.form.get("business_name") or "").strip()
            owner_name = (request.form.get("owner_name") or "").strip()
            email = (request.form.get("email") or "").lower().strip()
            phone = (request.form.get("phone") or "").strip()
            category = (request.form.get("category") or "").strip()
            service_area = (request.form.get("service_area") or "").strip()
            address = (request.form.get("address") or "").strip()
            password = request.form.get("password") or ""

            if not business_name or not owner_name or not email or not phone or not category or not password:
                flash("All required partner fields are required.", "error")
                return redirect(url_for("partner_register"))

            existing_partner = Partner.query.filter(
                (Partner.email == email) | (Partner.phone == phone)
            ).first()

            if existing_partner:
                flash("Partner email or phone already registered.", "error")
                return redirect(url_for("partner_login"))

            partner = Partner(
                business_name=business_name,
                owner_name=owner_name,
                email=email,
                phone=phone,
                category=category,
                service_area=service_area,
                address=address,
                password_hash=generate_password_hash(password),
                status="Pending"
            )

            db.session.add(partner)
            db.session.commit()

            flash("Partner application submitted. Admin approval is required.", "success")
            return redirect(url_for("partner_login"))

        return render_template("partner_register.html")


    @app.route("/partner/login", methods=["GET", "POST"])
    def partner_login():
        if request.method == "POST":
            email = (request.form.get("email") or "").lower().strip()
            password = request.form.get("password") or ""

            if not email or not password:
                flash("Email and password are required.", "error")
                return redirect(url_for("partner_login"))

            partner = Partner.query.filter_by(email=email).first()

            if not partner or not check_password_hash(partner.password_hash, password):
                flash("Invalid partner email or password.", "error")
                return redirect(url_for("partner_login"))

            if partner.status != "Approved":
                flash("Your partner account is awaiting admin approval.", "error")
                return redirect(url_for("partner_login"))

            session["partner_id"] = partner.id

            flash("Partner logged in successfully.", "success")
            return redirect(url_for("partner_dashboard"))

        return render_template("partner_login.html")


    @app.route("/partner/logout")
    def partner_logout():
        session.pop("partner_id", None)
        flash("Partner logged out successfully.", "success")
        return redirect(url_for("partner_login"))


    @app.route("/partner/dashboard")
    def partner_dashboard():
        partner_id = session.get("partner_id")

        if not partner_id:
            flash("Please login as partner.", "error")
            return redirect(url_for("partner_login"))

        partner = Partner.query.get_or_404(partner_id)

        return render_template(
            "partner_dashboard.html",
            partner=partner
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            email = (request.form.get("email") or "").lower().strip()
            phone = (request.form.get("phone") or "").strip()
            password = request.form.get("password") or ""

            if not name or not email or not phone or not password:
                flash("All fields are required.", "error")
                return redirect(url_for("register"))

            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please login.", "error")
                return redirect(url_for("login"))

            if User.query.filter_by(phone=phone).first():
                flash("Mobile number already registered. Please login.", "error")
                return redirect(url_for("login"))

            user = User(
                name=name,
                email=email,
                phone=phone,
                password_hash=generate_password_hash(password),
                role="customer",
                wallet_balance=0,
                referral_code=generate_referral_code(name),
            )

            db.session.add(user)
            db.session.commit()

            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (
                request.form.get("username")
                or request.form.get("email")
                or ""
            ).strip()

            password = request.form.get("password") or ""

            if not username or not password:
                flash("Mobile number/email and password are required.", "error")
                return redirect(url_for("login"))

            user = User.query.filter_by(email=username.lower()).first()

            if not user:
                user = User.query.filter_by(phone=username).first()

            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid mobile number/email or password.", "error")
                return redirect(url_for("login"))

            if user.role == "customer" and not user.referral_code:
                user.referral_code = generate_referral_code(user.name)
                db.session.commit()

            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            if user.role == "technician":
                return redirect(url_for("technician_dashboard"))

            return redirect(url_for("customer_dashboard"))

        return render_template("login.html")

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()

            user = User.query.filter_by(email=username.lower()).first()

            if not user:
                user = User.query.filter_by(phone=username).first()

            if not user:
                flash("No account found with this email/mobile.", "error")
                return redirect(url_for("forgot_password"))

            return redirect(url_for("reset_password", user_id=user.id))

        return render_template("forgot_password.html")

    @app.route("/reset-password/<int:user_id>", methods=["GET", "POST"])
    def reset_password(user_id):
        user = User.query.get_or_404(user_id)

        if request.method == "POST":
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""

            if not password or not confirm_password:
                flash("Both password fields are required.", "error")
                return redirect(url_for("reset_password", user_id=user.id))

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(url_for("reset_password", user_id=user.id))

            user.password_hash = generate_password_hash(password)
            db.session.commit()

            flash("Password reset successfully. Please login.", "success")
            return redirect(url_for("login"))

        return render_template("reset_password.html", user=user)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "success")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def customer_dashboard():
        if current_user.role != "customer":
            return redirect(url_for("index"))

        if not current_user.referral_code:
            current_user.referral_code = generate_referral_code(current_user.name)
            db.session.commit()

        bookings = Booking.query.filter_by(
            customer_id=current_user.id
        ).order_by(
            Booking.created_at.desc()
        ).all()

        tickets = SupportTicket.query.filter_by(
            customer_id=current_user.id
        ).order_by(
            SupportTicket.created_at.desc()
        ).all()

        return render_template(
            "customer_dashboard.html",
            bookings=bookings,
            tickets=tickets
        )

    @app.route("/create-ticket", methods=["POST"])
    @login_required
    def create_ticket():
        if current_user.role != "customer":
            flash("Only customers can create support tickets.", "error")
            return redirect(url_for("index"))

        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()
        booking_id = request.form.get("booking_id") or None

        if not subject or not message:
            flash("Subject and message are required.", "error")
            return redirect(url_for("customer_dashboard"))

        ticket = SupportTicket(
            customer_id=current_user.id,
            booking_id=booking_id,
            subject=subject,
            message=message,
            status="Open"
        )

        db.session.add(ticket)
        db.session.commit()

        flash("Support ticket submitted successfully.", "success")
        return redirect(url_for("customer_dashboard"))

    @app.route("/book", methods=["GET", "POST"])
    @login_required
    def book():
        if current_user.role != "customer":
            flash("Only customers can book services.", "error")
            return redirect(url_for("index"))

        all_services = Service.query.all()
        services = all_services

        selected_service_id = request.args.get("service_id")
        selected_service = None

        if selected_service_id:
            selected_service = Service.query.get(selected_service_id)

            if selected_service:
                services = Service.query.filter_by(
                    category=selected_service.category
                ).all()

        if request.method == "POST":
            service_ids = request.form.get("service_ids", "")

            service_id_list = [
                int(service_id)
                for service_id in service_ids.split(",")
                if service_id.strip().isdigit()
            ]

            if not service_id_list:
                flash("Please select at least one service.", "error")
                return redirect(url_for("book"))

            coupon_code = (request.form.get("coupon_code") or "").strip()

            payment_method = (
                request.form.get("payment_choice")
                or request.form.get("payment_method")
                or "Cash After Service"
            ).strip()

            referral_code = (
                request.form.get("referral_code") or ""
            ).strip().upper()

            referrer = None

            if referral_code:
                referrer = User.query.filter_by(
                    referral_code=referral_code
                ).first()

                if not referrer:
                    flash("Invalid referral code.", "error")
                    return redirect(url_for("book"))

                if referrer.id == current_user.id:
                    flash("You cannot use your own referral code.", "error")
                    return redirect(url_for("book"))

            try:
                discount = int(float(request.form.get("discount") or 0))
            except ValueError:
                discount = 0

            if referrer:
                discount += 100
                coupon_code = (
                    coupon_code + " + REFERRAL100"
                    if coupon_code
                    else "REFERRAL100"
                )

            selected_services = Service.query.filter(
                Service.id.in_(service_id_list)
            ).all()

            if not selected_services:
                flash("Selected services are not available.", "error")
                return redirect(url_for("book"))

            subtotal = sum(service.price for service in selected_services)
            gst = int(round(subtotal * 0.18))
            final_total = max(0, subtotal + gst - discount)

            per_booking_discount = 0

            if selected_services and discount > 0:
                per_booking_discount = int(discount / len(selected_services))

            created_booking_ids = []

            for service in selected_services:
                service_gst = int(round(service.price * 0.18))
                service_total = max(
                    0,
                    service.price + service_gst - per_booking_discount
                )

                latitude = request.form.get("latitude")
                longitude = request.form.get("longitude")

                map_link = None

                if latitude and longitude:
                    map_link = f"https://www.google.com/maps?q={latitude},{longitude}"

                building_no = request.form.get("building_no")
                floor = request.form.get("floor")
                landmark = request.form.get("landmark")

                full_address = (
                    f"Building/Flat: {building_no or ''}, "
                    f"Floor: {floor or ''}, "
                    f"Landmark: {landmark or ''}"
                )

                online_payment = payment_method in [
                    "UPI",
                    "Card",
                    "Online Payment",
                    "Razorpay",
                ]

                booking = Booking(
                    customer_id=current_user.id,
                    service_id=service.id,
                    customer_name=request.form.get("customer_name"),
                    phone=request.form.get("phone"),
                    address=full_address,
                    building_no=building_no,
                    floor=floor,
                    landmark=landmark,
                    latitude=latitude,
                    longitude=longitude,
                    map_link=map_link,
                    booking_date=request.form.get("booking_date"),
                    booking_time=request.form.get("booking_time"),
                    notes=request.form.get("notes"),
                    status="Pending",
                    payment_status="Pending" if online_payment else "Unpaid",
                    coupon_code=coupon_code,
                    referral_code_used=referral_code if referrer else None,
                    referred_by_user_id=referrer.id if referrer else None,
                    referral_reward_given=False,
                    discount=per_booking_discount,
                    payment_method=payment_method,
                    total_amount=service_total,
                    gst_amount=service_gst,
                    customer_notification=(
                        "Your booking has been created. Admin will assign a technician soon."
                    ),
                    notification_read=False,
                )

                db.session.add(booking)
                db.session.flush()

                booking.invoice_number = f"INV-2026-{booking.id:04d}"
                created_booking_ids.append(booking.id)

            db.session.commit()

            booking_ids_text = ",".join(str(item) for item in created_booking_ids)

            if payment_method in ["UPI", "Card", "Online Payment", "Razorpay"]:
                razorpay_client = get_razorpay_client()

                if not razorpay_client:
                    flash("Razorpay keys are missing. Please check your .env file.", "error")
                    return redirect(url_for("customer_dashboard"))

                try:
                    razorpay_order = razorpay_client.order.create({
                        "amount": int(final_total) * 100,
                        "currency": "INR",
                        "receipt": f"RRCP-{created_booking_ids[0]}",
                        "payment_capture": 1,
                    })

                    bookings = Booking.query.filter(
                        Booking.id.in_(created_booking_ids)
                    ).all()

                    for booking in bookings:
                        booking.razorpay_order_id = razorpay_order["id"]

                    db.session.commit()

                    return redirect(
                        url_for(
                            "razorpay_payment",
                            booking_ids=booking_ids_text,
                            total=final_total
                        )
                    )

                except Exception as error:
                    flash(f"Razorpay order creation failed: {error}", "error")
                    return redirect(url_for("customer_dashboard"))

            return redirect(
                url_for(
                    "booking_success",
                    booking_ids=booking_ids_text,
                    total=final_total,
                    payment_method=payment_method
                )
            )

        return render_template(
            "booking.html",
            services=services,
            selected_service_id=selected_service_id,
            selected_service=selected_service
        )

    @app.route("/razorpay-payment")
    @login_required
    def razorpay_payment():
        if current_user.role != "customer":
            flash("Only customers can make payments.", "error")
            return redirect(url_for("index"))

        booking_ids = request.args.get("booking_ids", "")
        total = int(float(request.args.get("total", "0")))

        booking_id_list = [
            int(item)
            for item in booking_ids.split(",")
            if item.strip().isdigit()
        ]

        bookings = Booking.query.filter(
            Booking.id.in_(booking_id_list),
            Booking.customer_id == current_user.id
        ).all()

        if not bookings:
            flash("Booking not found.", "error")
            return redirect(url_for("customer_dashboard"))

        razorpay_order_id = bookings[0].razorpay_order_id

        if not razorpay_order_id:
            flash("Payment order not found.", "error")
            return redirect(url_for("customer_dashboard"))

        key_id = current_app.config.get("RAZORPAY_KEY_ID")

        return render_template_string(
            """
            {% extends "layout.html" %}
            {% block content %}
            <section class="receipt-page">
                <div class="receipt-card">
                    <div class="receipt-title">
                        <h1>RR CLAN PRO</h1>
                        <p>Secure Online Payment</p>
                        <div class="receipt-status">Pay ₹{{ total }}</div>
                    </div>

                    <div class="receipt-divider"></div>

                    <h3>Booking Summary</h3>

                    {% for booking in bookings %}
                    <div class="receipt-service-row">
                        <span>#RRCP-{{ booking.id }} - {{ booking.service.name }}</span>
                        <strong>₹{{ booking.total_amount }}</strong>
                    </div>
                    {% endfor %}

                    <div class="receipt-total-row receipt-payable">
                        <span>Total Payable</span>
                        <strong>₹{{ total }}</strong>
                    </div>

                    <form method="POST" action="{{ url_for('razorpay_success') }}" id="paymentSuccessForm">
                        <input type="hidden" name="booking_ids" value="{{ booking_ids }}">
                        <input type="hidden" name="razorpay_payment_id" id="razorpay_payment_id">
                        <input type="hidden" name="razorpay_order_id" id="razorpay_order_id">
                        <input type="hidden" name="razorpay_signature" id="razorpay_signature">
                    </form>

                    <div class="receipt-actions">
                        <button id="rzp-button" class="btn-black">Pay Now</button>
                        <a href="{{ url_for('customer_dashboard') }}" class="btn-white">Pay Later</a>
                    </div>
                </div>
            </section>

            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

            <script>
            const options = {
                "key": "{{ key_id }}",
                "amount": "{{ total * 100 }}",
                "currency": "INR",
                "name": "RR CLAN PRO",
                "description": "Home & Property Service Payment",
                "order_id": "{{ razorpay_order_id }}",
                "handler": function (response) {
                    document.getElementById("razorpay_payment_id").value = response.razorpay_payment_id;
                    document.getElementById("razorpay_order_id").value = response.razorpay_order_id;
                    document.getElementById("razorpay_signature").value = response.razorpay_signature;
                    document.getElementById("paymentSuccessForm").submit();
                },
                "prefill": {
                    "name": "{{ current_user.name }}",
                    "email": "{{ current_user.email }}",
                    "contact": "{{ current_user.phone or '' }}"
                },
                "theme": {
                    "color": "#000000"
                }
            };

            const rzp = new Razorpay(options);

            document.getElementById("rzp-button").onclick = function(e){
                rzp.open();
                e.preventDefault();
            }
            </script>
            {% endblock %}
            """,
            bookings=bookings,
            booking_ids=booking_ids,
            total=total,
            key_id=key_id,
            razorpay_order_id=razorpay_order_id
        )

    @app.route("/razorpay-success", methods=["POST"])
    @login_required
    def razorpay_success():
        if current_user.role != "customer":
            flash("Only customers can verify payment.", "error")
            return redirect(url_for("index"))

        booking_ids = request.form.get("booking_ids", "")
        razorpay_payment_id = request.form.get("razorpay_payment_id")
        razorpay_order_id = request.form.get("razorpay_order_id")
        razorpay_signature = request.form.get("razorpay_signature")

        booking_id_list = [
            int(item)
            for item in booking_ids.split(",")
            if item.strip().isdigit()
        ]

        bookings = Booking.query.filter(
            Booking.id.in_(booking_id_list),
            Booking.customer_id == current_user.id
        ).all()

        if not bookings:
            flash("Booking not found.", "error")
            return redirect(url_for("customer_dashboard"))

        razorpay_client = get_razorpay_client()

        if not razorpay_client:
            flash("Razorpay keys are missing.", "error")
            return redirect(url_for("customer_dashboard"))

        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })

            total = 0

            for booking in bookings:
                booking.payment_status = "Paid"
                booking.payment_method = "Online Payment"
                booking.razorpay_order_id = razorpay_order_id
                booking.razorpay_payment_id = razorpay_payment_id
                booking.razorpay_signature = razorpay_signature
                booking.notification_read = False
                booking.customer_notification = (
                    f"Online payment received for {booking.service.name}. "
                    "Admin will assign a technician soon."
                )

                total += booking.total_amount or 0

            db.session.commit()

            flash("Payment successful.", "success")

            return redirect(
                url_for(
                    "booking_success",
                    booking_ids=booking_ids,
                    total=total,
                    payment_method="Online Payment"
                )
            )

        except Exception:
            for booking in bookings:
                booking.payment_status = "Failed"
                booking.customer_notification = (
                    "Payment failed. You can retry payment or contact RR CLAN PRO support."
                )

            db.session.commit()

            flash("Payment verification failed.", "error")
            return redirect(url_for("customer_dashboard"))

    @app.route("/booking-success")
    @login_required
    def booking_success():
        if current_user.role != "customer":
            flash("Only customers can view booking success.", "error")
            return redirect(url_for("index"))

        booking_ids = request.args.get("booking_ids", "")
        total = request.args.get("total", "0")
        payment_method = request.args.get("payment_method", "Cash After Service")

        booking_id_list = [
            int(item)
            for item in booking_ids.split(",")
            if item.strip().isdigit()
        ]

        bookings = Booking.query.filter(
            Booking.id.in_(booking_id_list),
            Booking.customer_id == current_user.id
        ).all()

        if not bookings:
            flash("Booking details not found.", "error")
            return redirect(url_for("customer_dashboard"))

        return render_template(
            "booking_success.html",
            bookings=bookings,
            total=total,
            payment_method=payment_method
        )

    @app.route("/download_invoice/<int:booking_id>")
    @login_required
    def download_invoice(booking_id):
        booking = Booking.query.get_or_404(booking_id)

        if current_user.role != "admin" and booking.customer_id != current_user.id:
            flash("Access denied.", "error")
            return redirect(url_for("customer_dashboard"))

        gst_amount = booking.gst_amount or int(round(booking.service.price * 0.18))
        total_amount = booking.total_amount or int(round(booking.service.price * 1.18))

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 30px;
                    color: #111;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #111;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                }}
                .box {{
                    border: 1px solid #ccc;
                    padding: 15px;
                    margin-bottom: 15px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 10px;
                    text-align: left;
                }}
                th {{
                    background: #f3f3f3;
                }}
                .total {{
                    font-size: 18px;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>RR CLAN PRO</h1>
                <p>Professional Home & Property Services</p>
                <h3>Tax Invoice</h3>
            </div>

            <div class="box">
                <p><b>Invoice No:</b> {booking.invoice_number or f"INV-{booking.id}"}</p>
                <p><b>Booking ID:</b> #RRCP-{booking.id}</p>
                <p><b>Date:</b> {booking.booking_date}</p>
                <p><b>Time:</b> {booking.booking_time}</p>
            </div>

            <div class="box">
                <p><b>Customer Name:</b> {booking.customer_name}</p>
                <p><b>Phone:</b> {booking.phone}</p>
                <p><b>Address:</b> {booking.address}</p>
            </div>

            <table>
                <tr>
                    <th>Service</th>
                    <th>Base Price</th>
                    <th>GST</th>
                    <th>Discount</th>
                    <th>Total</th>
                </tr>
                <tr>
                    <td>{booking.service.name}</td>
                    <td>Rs. {booking.service.price}</td>
                    <td>Rs. {gst_amount}</td>
                    <td>Rs. {booking.discount or 0}</td>
                    <td>Rs. {total_amount}</td>
                </tr>
            </table>

            <div class="box">
                <p><b>Payment Method:</b> {booking.payment_method or "Cash After Service"}</p>
                <p><b>Payment Status:</b> {booking.payment_status or "Unpaid"}</p>
                <p class="total"><b>Total Amount:</b> Rs. {total_amount}</p>
            </div>

            <div class="footer">
                <p>Thank you for choosing RR CLAN PRO.</p>
                <p>This is a computer generated invoice.</p>
            </div>
        </body>
        </html>
        """

        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf)

        if pisa_status.err:
            flash("Could not generate invoice PDF.", "error")
            return redirect(url_for("customer_dashboard"))

        response = make_response(pdf.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f"attachment; filename=RRCP-Invoice-{booking.id}.pdf"
        )

        return response

    @app.route("/admin")
    @login_required
    def admin_dashboard():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        technicians = User.query.filter_by(role="technician").all()
        notifications = Booking.query.filter_by(notification_read=False).count()

        customers_count = User.query.filter_by(role="customer").count()

        referral_customers = Booking.query.filter(
            Booking.referred_by_user_id.isnot(None)
        ).count()

        repeat_customers = (
            db.session.query(Booking.customer_id)
            .group_by(Booking.customer_id)
            .having(db.func.count(Booking.id) > 1)
            .count()
        )

        open_tickets = SupportTicket.query.filter_by(status="Open").count()
        pending_partners = Partner.query.filter_by(status="Pending").count()

        return render_template(
            "admin_dashboard.html",
            bookings=bookings,
            technicians=technicians,
            notifications=notifications,
            customers_count=customers_count,
            referral_customers=referral_customers,
            repeat_customers=repeat_customers,
            open_tickets=open_tickets,
            pending_partners=pending_partners
        )

    @app.route("/admin/support")
    @login_required
    def admin_support():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        tickets = SupportTicket.query.order_by(
            SupportTicket.created_at.desc()
        ).all()

        return render_template(
            "admin_support.html",
            tickets=tickets
        )


    @app.route("/admin/partners")
    @login_required
    def admin_partners():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        partners = Partner.query.order_by(
            Partner.created_at.desc()
        ).all()

        return render_template(
            "admin_partners.html",
            partners=partners
        )


    @app.route("/admin/partner/approve/<int:partner_id>", methods=["POST"])
    @login_required
    def approve_partner(partner_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        partner = Partner.query.get_or_404(partner_id)

        partner.status = "Approved"
        db.session.commit()

        flash("Partner approved successfully.", "success")
        return redirect(url_for("admin_partners"))


    @app.route("/admin/partner/reject/<int:partner_id>", methods=["POST"])
    @login_required
    def reject_partner(partner_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        partner = Partner.query.get_or_404(partner_id)

        partner.status = "Rejected"
        db.session.commit()

        flash("Partner rejected successfully.", "success")
        return redirect(url_for("admin_partners"))


    @app.route("/admin/partner/delete/<int:partner_id>", methods=["POST"])
    @login_required
    def delete_partner(partner_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        partner = Partner.query.get_or_404(partner_id)

        db.session.delete(partner)
        db.session.commit()

        flash("Partner deleted successfully.", "success")
        return redirect(url_for("admin_partners"))

    @app.route("/reply-ticket/<int:ticket_id>", methods=["POST"])
    @login_required
    def reply_ticket(ticket_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        ticket = SupportTicket.query.get_or_404(ticket_id)

        ticket.admin_reply = request.form.get("reply")
        ticket.status = "Resolved"

        db.session.commit()

        flash("Reply sent successfully.", "success")
        return redirect(url_for("admin_support"))

    @app.route("/admin/payment/received/<int:booking_id>", methods=["POST"])
    @login_required
    def mark_payment_received(booking_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        booking = Booking.query.get_or_404(booking_id)

        booking.payment_status = "Paid"
        booking.notification_read = False
        booking.customer_notification = (
            f"Payment received for {booking.service.name}. Thank you for choosing RR CLAN PRO."
        )

        db.session.commit()

        flash("Payment marked as received.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/data")
    @login_required
    def admin_data():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        customers = User.query.filter_by(role="customer").all()
        technicians = User.query.filter_by(role="technician").all()
        services = Service.query.all()
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        partners = Partner.query.order_by(Partner.created_at.desc()).all()

        return render_template(
            "admin_data.html",
            customers=customers,
            technicians=technicians,
            services=services,
            bookings=bookings,
            partners=partners
        )

    @app.route("/admin/customer/<int:customer_id>")
    @login_required
    def customer_history(customer_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        customer = User.query.get_or_404(customer_id)

        if customer.role != "customer":
            flash("Selected user is not a customer.", "error")
            return redirect(url_for("admin_data"))

        bookings = Booking.query.filter_by(
            customer_id=customer.id
        ).order_by(
            Booking.created_at.desc()
        ).all()

        return render_template(
            "customer_history.html",
            customer=customer,
            bookings=bookings
        )

    @app.route("/admin/customer/delete/<int:customer_id>", methods=["POST"])
    @login_required
    def delete_customer(customer_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        customer = User.query.get_or_404(customer_id)

        if customer.role != "customer":
            flash("Only customer accounts can be deleted here.", "error")
            return redirect(url_for("admin_data"))

        bookings = Booking.query.filter_by(customer_id=customer.id).all()

        for booking in bookings:
            db.session.delete(booking)

        db.session.delete(customer)
        db.session.commit()

        flash("Customer and related bookings deleted successfully.", "success")
        return redirect(url_for("admin_data"))

    @app.route("/admin/technician/add", methods=["POST"])
    @login_required
    def add_technician():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").lower().strip()
        phone = (request.form.get("phone") or "").strip()
        skill = (request.form.get("skill") or "").strip()
        password = request.form.get("password") or ""

        if not name or not email or not phone or not skill or not password:
            flash("All technician fields are required.", "error")
            return redirect(url_for("admin_data"))

        existing_user = User.query.filter(
            (User.email == email) | (User.phone == phone)
        ).first()

        if existing_user:
            flash("Technician email or mobile already exists.", "error")
            return redirect(url_for("admin_data"))

        technician = User(
            name=name,
            email=email,
            phone=phone,
            skill=skill,
            password_hash=generate_password_hash(password),
            role="technician"
        )

        db.session.add(technician)
        db.session.commit()

        flash("Technician added successfully.", "success")
        return redirect(url_for("admin_data"))

    @app.route("/admin/service/add", methods=["POST"])
    @login_required
    def add_service():
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        clan = (request.form.get("clan") or "").strip()
        category = (request.form.get("category") or "General").strip()
        name = (request.form.get("name") or "").strip()
        price = (request.form.get("price") or "").strip()
        duration = (request.form.get("duration") or "").strip()
        description = (request.form.get("description") or "").strip()
        image = (request.form.get("image") or "default.jpg").strip()
        skill_required = (request.form.get("skill_required") or "").strip()

        if not clan or not category or not name or not price or not duration or not skill_required:
            flash("All required service fields are required.", "error")
            return redirect(url_for("admin_data"))

        service = Service(
            clan=clan,
            category=category,
            name=name,
            price=int(price),
            duration=duration,
            description=description,
            image=image,
            skill_required=skill_required
        )

        db.session.add(service)
        db.session.commit()

        flash("Service added successfully.", "success")
        return redirect(url_for("admin_data"))

    @app.route("/admin/service/update/<int:service_id>", methods=["POST"])
    @login_required
    def update_service(service_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        service = Service.query.get_or_404(service_id)

        service.clan = (request.form.get("clan") or service.clan).strip()
        service.category = (request.form.get("category") or service.category).strip()
        service.name = (request.form.get("name") or service.name).strip()
        service.price = int(request.form.get("price") or service.price)
        service.duration = (request.form.get("duration") or service.duration).strip()
        service.description = (request.form.get("description") or service.description).strip()
        service.image = (request.form.get("image") or service.image).strip()
        service.skill_required = (
            request.form.get("skill_required") or service.skill_required
        ).strip()

        db.session.commit()

        flash("Service updated successfully.", "success")
        return redirect(url_for("admin_data"))

    @app.route("/admin/service/delete/<int:service_id>", methods=["POST"])
    @login_required
    def delete_service(service_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        service = Service.query.get_or_404(service_id)

        existing_bookings = Booking.query.filter_by(
            service_id=service.id
        ).count()

        if existing_bookings > 0:
            flash(
                "Cannot delete this service because bookings already exist for it.",
                "error"
            )
            return redirect(url_for("admin_data"))

        db.session.delete(service)
        db.session.commit()

        flash("Service deleted successfully.", "success")
        return redirect(url_for("admin_data"))
    
    @app.route("/assign/<int:booking_id>", methods=["POST"])
    @login_required
    def assign_booking(booking_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        booking = Booking.query.get_or_404(booking_id)
        technician_id = request.form.get("technician_id")
        technician = User.query.get_or_404(technician_id)

        booking.technician_id = technician.id
        booking.status = "Assigned"
        booking.notification_read = False
        booking.technician_notification = (
            f"New job assigned: {booking.service.name}, "
            f"Customer: {booking.customer_name}, "
            f"Date: {booking.booking_date}, "
            f"Time: {booking.booking_time}"
        )
        booking.customer_notification = (
            f"{technician.name} has been assigned for your {booking.service.name} service."
        )

        db.session.commit()

        flash(
            f"Booking assigned to {technician.name}. Technician notification created.",
            "success"
        )
        return redirect(url_for("admin_dashboard"))

    @app.route("/technician")
    @login_required
    def technician_dashboard():
        if current_user.role != "technician":
            flash("Technician access only.", "error")
            return redirect(url_for("index"))

        jobs = Booking.query.filter_by(
            technician_id=current_user.id
        ).order_by(
            Booking.created_at.desc()
        ).all()

        return render_template("technician_dashboard.html", jobs=jobs)

    @app.route("/job/<int:booking_id>/<action>")
    @login_required
    def update_job_status(booking_id, action):
        if current_user.role != "technician":
            flash("Technician access only.", "error")
            return redirect(url_for("index"))

        booking = Booking.query.get_or_404(booking_id)

        if booking.technician_id != current_user.id:
            flash("This job is not assigned to you.", "error")
            return redirect(url_for("technician_dashboard"))

        allowed_actions = {
            "accept": "Accepted",
            "reject": "Rejected",
            "complete": "Completed",
        }

        if action in allowed_actions:
            booking.status = allowed_actions[action]
            booking.notification_read = False

            if action == "accept":
                booking.customer_notification = (
                    f"{current_user.name} accepted your job for {booking.service.name}. "
                    f"Technician will visit on {booking.booking_date} at {booking.booking_time}."
                )

            elif action == "reject":
                booking.customer_notification = (
                    f"{current_user.name} rejected the job for {booking.service.name}. "
                    "Admin will assign another technician shortly."
                )

            elif action == "complete":
                booking.customer_notification = (
                    f"Your {booking.service.name} service has been completed. Please rate your experience."
                )

                if booking.referred_by and not booking.referral_reward_given:
                    booking.referred_by.wallet_balance += 200
                    booking.referral_reward_given = True

            db.session.commit()
            flash(f"Job marked as {allowed_actions[action]}.", "success")

        return redirect(url_for("technician_dashboard"))

    @app.route("/collect-payment/<int:booking_id>")
    @login_required
    def collect_payment(booking_id):
        if current_user.role != "technician":
            flash("Technician access only.", "error")
            return redirect(url_for("index"))

        booking = Booking.query.get_or_404(booking_id)

        if booking.technician_id != current_user.id:
            flash("This job is not assigned to you.", "error")
            return redirect(url_for("technician_dashboard"))

        booking.payment_status = "Paid"
        booking.notification_read = False
        booking.customer_notification = (
            f"Cash payment received for {booking.service.name}. "
            "Thank you for choosing RR CLAN PRO."
        )

        db.session.commit()

        flash("Cash payment collected successfully.", "success")
        return redirect(url_for("technician_dashboard"))

    @app.route("/rate/<int:booking_id>", methods=["POST"])
    @login_required
    def rate_booking(booking_id):
        if current_user.role != "customer":
            flash("Only customers can rate services.", "error")
            return redirect(url_for("index"))

        booking = Booking.query.get_or_404(booking_id)

        if booking.customer_id != current_user.id:
            flash("You cannot rate this booking.", "error")
            return redirect(url_for("customer_dashboard"))

        if booking.status != "Completed":
            flash("You can rate only completed services.", "error")
            return redirect(url_for("customer_dashboard"))

        if booking.rating:
            flash("You have already rated this service.", "error")
            return redirect(url_for("customer_dashboard"))

        rating = request.form.get("rating")
        review = request.form.get("review")

        if not rating:
            flash("Please select a rating.", "error")
            return redirect(url_for("customer_dashboard"))

        booking.rating = int(rating)
        booking.review = review
        booking.notification_read = False
        booking.customer_notification = "Thank you for rating your RR CLAN PRO service."

        db.session.commit()

        flash("Thank you for rating this service.", "success")
        return redirect(url_for("customer_dashboard"))

    @app.route("/admin/service/force-delete/<int:service_id>", methods=["POST"])
    @login_required
    def force_delete_service(service_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        service = Service.query.get_or_404(service_id)

        Booking.query.filter_by(service_id=service.id).delete()

        db.session.delete(service)
        db.session.commit()

        flash("Service deleted successfully.", "success")

        return redirect(url_for("admin_data"))


    @app.route("/admin/technician/force-delete/<int:technician_id>", methods=["POST"])
    @login_required
    def force_delete_technician(technician_id):
        if current_user.role != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("index"))

        technician = User.query.get_or_404(technician_id)

        if technician.role != "technician":
            flash("Only technicians can be deleted here.", "error")
            return redirect(url_for("admin_data"))

        Booking.query.filter_by(
            technician_id=technician.id
        ).update({
            "technician_id": None,
            "status": "Pending",
            "notification_read": False,
            "technician_notification": "No technician assigned yet",
            "customer_notification": "Technician removed. Admin will assign another technician shortly."
        })

        db.session.delete(technician)
        db.session.commit()

        flash(
            "Technician deleted and all assigned jobs moved back to Pending.",
            "success"
        )

        return redirect(url_for("admin_data"))


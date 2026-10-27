import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-this-secret-before-deploying")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0").lower() in {"1", "true", "yes"}
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "mysql+pymysql://retrieve_user:change_me@localhost/retrieve_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("Item", backref="owner", lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)
    item_type = db.Column(db.String(10), nullable=False, index=True)  # lost / found
    location = db.Column(db.String(180), nullable=False, index=True)
    item_date = db.Column(db.Date, nullable=True)
    image_filename = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item = db.relationship("Item", backref="claims")
    claimant = db.relationship("User", foreign_keys=[claimant_id])

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(255), nullable=False, default="/")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.relationship("User", backref=db.backref("notifications", lazy=True))

class ItemMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lost_item = db.relationship("Item", foreign_keys=[lost_item_id])
    found_item = db.relationship("Item", foreign_keys=[found_item_id])
    __table_args__ = (db.UniqueConstraint("lost_item_id", "found_item_id", name="uq_lost_found_match"),)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    body = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    item = db.relationship("Item")
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])

def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


@app.after_request
def add_security_headers(response):
    """Set conservative browser security headers without breaking inline page scripts."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

@app.context_processor
def inject_user():
    user = current_user()
    unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count() if user else 0
    unread_messages = Message.query.filter_by(recipient_id=user.id, is_read=False).count() if user else 0
    return {"current_user": user, "unread_notifications": unread_notifications, "unread_messages": unread_messages}

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please sign in to continue.", "info")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_notification(user_id, title, body, url):
    db.session.add(Notification(user_id=user_id, title=title, body=body, url=url))

def match_score(a, b):
    """Explainable starter matcher; this is ranking assistance, not proof of ownership."""
    score = 0
    if a.category.lower() == b.category.lower():
        score += 30
    a_words = set((a.title + " " + a.description).lower().replace("-", " ").split())
    b_words = set((b.title + " " + b.description).lower().replace("-", " ").split())
    stop = {"the", "and", "for", "with", "that", "this", "from", "have", "was", "are", "item", "lost", "found"}
    a_words -= stop
    b_words -= stop
    if a_words or b_words:
        overlap = len(a_words & b_words) / max(1, len(a_words | b_words))
        score += round(overlap * 35)
    if a.location.lower().strip() == b.location.lower().strip():
        score += 25
    elif a.location.lower().split() and b.location.lower().split() and set(a.location.lower().split()) & set(b.location.lower().split()):
        score += 12
    if a.item_date and b.item_date:
        days = abs((a.item_date - b.item_date).days)
        score += 10 if days <= 2 else 5 if days <= 7 else 0
    return min(score, 100)

def find_matches_for(item):
    opposite = "found" if item.item_type == "lost" else "lost"
    candidates = Item.query.filter_by(status="open", item_type=opposite, category=item.category).filter(Item.id != item.id).all()
    for other in candidates:
        score = match_score(item, other)
        if score < 25:
            continue
        lost = item if item.item_type == "lost" else other
        found = item if item.item_type == "found" else other
        exists = ItemMatch.query.filter_by(lost_item_id=lost.id, found_item_id=found.id).first()
        if exists:
            continue
        db.session.add(ItemMatch(lost_item_id=lost.id, found_item_id=found.id, score=score))
        create_notification(lost.user_id, "A possible item match was found", f"'{found.title}' may match your report '{lost.title}' ({score}% match). Please verify the details.", url_for("matches"))
        if found.user_id != lost.user_id:
            create_notification(found.user_id, "A possible item match was found", f"'{lost.title}' may match your found report '{found.title}' ({score}% match). Please verify the details.", url_for("matches"))

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    item_type = request.args.get("type", "").strip()
    category = request.args.get("category", "").strip()
    items_query = Item.query.filter_by(status="open")
    if query:
        term = f"%{query}%"
        items_query = items_query.filter(db.or_(Item.title.ilike(term), Item.description.ilike(term), Item.location.ilike(term)))
    if item_type in {"lost", "found"}:
        items_query = items_query.filter_by(item_type=item_type)
    if category:
        items_query = items_query.filter_by(category=category)
    items = items_query.order_by(Item.created_at.desc()).all()
    categories = ["Electronics", "Documents", "Wallets", "Keys", "Bags", "Clothing", "Jewellery", "Pets", "Other"]
    return render_template("index.html", items=items, q=query, selected_type=item_type, selected_category=category, categories=categories)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password of at least 8 characters.", "error")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("register.html")
        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        flash("Welcome to Retrieve. Your account is ready.", "success")
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            flash("You are signed in.", "success")
            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//") and "\\" not in next_url:
                return redirect(next_url)
            return redirect(url_for("index"))
        flash("Email or password was incorrect.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have signed out.", "info")
    return redirect(url_for("index"))

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    categories = ["Electronics", "Documents", "Wallets", "Keys", "Bags", "Clothing", "Jewellery", "Pets", "Other"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "Other")
        item_type = request.form.get("item_type", "")
        location = request.form.get("location", "").strip()
        date_str = request.form.get("item_date", "").strip()
        upload = request.files.get("image")
        if not title or not description or not location or item_type not in {"lost", "found"}:
            flash("Please complete all required fields.", "error")
            return render_template("report.html", categories=categories)
        filename = None
        if upload and upload.filename:
            if not allowed_file(upload.filename):
                flash("Image must be PNG, JPG, JPEG or WEBP.", "error")
                return render_template("report.html", categories=categories)
            original_name = secure_filename(upload.filename)
            stem = os.path.splitext(original_name)[0][:60] or "retrieve-image"
            filename = f"{stem}_{int(datetime.utcnow().timestamp())}.webp"
            target = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            try:
                from PIL import Image, ImageOps
                image = Image.open(upload.stream)
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                image.save(target, "WEBP", quality=82, method=6, optimize=True)
            except ImportError:
                # Pillow is included in requirements; this fallback keeps uploads functional if it is missing.
                upload.stream.seek(0)
                filename = f"{stem}_{int(datetime.utcnow().timestamp())}{os.path.splitext(original_name)[1].lower()}"
                target = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                upload.save(target)
            except Exception:
                flash("We couldn't read that image. Please choose a valid JPG, PNG or WEBP file.", "error")
                return render_template("report.html", categories=categories), 400
        item_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        item = Item(title=title, description=description, category=category, item_type=item_type,
                    location=location, item_date=item_date, image_filename=filename, user_id=current_user().id)
        db.session.add(item)
        db.session.commit()
        find_matches_for(item)
        db.session.commit()
        flash("Your report has been published. Retrieve checked for possible matches.", "success")
        return redirect(url_for("item_detail", item_id=item.id))
    return render_template("report.html", categories=categories)

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = db.get_or_404(Item, item_id)
    return render_template("item.html", item=item)

@app.route("/item/<int:item_id>/claim", methods=["POST"])
@login_required
def claim_item(item_id):
    item = db.get_or_404(Item, item_id)
    if item.user_id == current_user().id:
        flash("You cannot claim your own listing.", "error")
        return redirect(url_for("item_detail", item_id=item.id))
    message = request.form.get("message", "").strip()
    if len(message) < 10:
        flash("Please provide a little more detail so the reporter can verify your claim.", "error")
        return redirect(url_for("item_detail", item_id=item.id))
    claim = Claim(message=message, item_id=item.id, claimant_id=current_user().id)
    db.session.add(claim)
    create_notification(item.user_id, "New ownership claim", f"{current_user().name} submitted a claim for '{item.title}'. Review the private explanation in your dashboard.", url_for("dashboard"))
    db.session.commit()
    flash("Claim request sent. The reporter can review it from their dashboard.", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    my_items = Item.query.filter_by(user_id=user.id).order_by(Item.created_at.desc()).all()
    incoming_claims = Claim.query.join(Item).filter(Item.user_id == user.id).order_by(Claim.created_at.desc()).all()
    my_claims = Claim.query.filter_by(claimant_id=user.id).order_by(Claim.created_at.desc()).all()
    return render_template("dashboard.html", my_items=my_items, incoming_claims=incoming_claims, my_claims=my_claims)

@app.route("/claim/<int:claim_id>/<action>", methods=["POST"])
@login_required
def review_claim(claim_id, action):
    claim = db.get_or_404(Claim, claim_id)
    if claim.item.user_id != current_user().id:
        abort(403)
    if action not in {"approve", "reject"}:
        abort(400)
    claim.status = "approved" if action == "approve" else "rejected"
    if action == "approve":
        claim.item.status = "claimed"
    create_notification(claim.claimant_id, "Claim reviewed", f"Your claim for '{claim.item.title}' was {claim.status}.", url_for("dashboard"))
    db.session.commit()
    flash(f"Claim {claim.status}.", "success")
    return redirect(url_for("dashboard"))

@app.route("/item/<int:item_id>/close", methods=["POST"])
@login_required
def close_item(item_id):
    item = db.get_or_404(Item, item_id)
    if item.user_id != current_user().id:
        abort(403)
    item.status = "returned"
    db.session.commit()
    flash("Listing marked as returned.", "success")
    return redirect(url_for("dashboard"))

@app.route("/matches")
@login_required
def matches():
    user_id = current_user().id
    rows = ItemMatch.query.join(Item, db.or_(Item.id == ItemMatch.lost_item_id, Item.id == ItemMatch.found_item_id)).filter(
        db.or_(Item.user_id == user_id)
    ).order_by(ItemMatch.score.desc(), ItemMatch.created_at.desc()).all()
    # Keep only matches where the current user owns one side.
    rows = [m for m in rows if m.lost_item.user_id == user_id or m.found_item.user_id == user_id]
    return render_template("matches.html", matches=rows)

@app.route("/notifications")
@login_required
def notifications():
    rows = Notification.query.filter_by(user_id=current_user().id).order_by(Notification.created_at.desc()).all()
    for row in rows:
        row.is_read = True
    db.session.commit()
    return render_template("notifications.html", notifications=rows)

@app.route("/messages")
@login_required
def messages():
    uid = current_user().id
    rows = Message.query.filter(db.or_(Message.sender_id == uid, Message.recipient_id == uid)).order_by(Message.created_at.desc()).all()
    # Show one latest message per item/other participant conversation.
    seen, conversations = set(), []
    for msg in rows:
        other_id = msg.recipient_id if msg.sender_id == uid else msg.sender_id
        key = (msg.item_id, min(uid, other_id), max(uid, other_id))
        if key not in seen:
            seen.add(key)
            conversations.append(msg)
    return render_template("messages.html", messages=conversations)

@app.route("/messages/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def item_messages(item_id):
    item = db.get_or_404(Item, item_id)
    user = current_user()
    if user.id == item.user_id:
        other_ids = db.session.query(Claim.claimant_id).filter_by(item_id=item.id).all()
        allowed_ids = {row[0] for row in other_ids}
        other_id = request.args.get("with", type=int)
        if other_id not in allowed_ids:
            abort(403)
    else:
        claim = Claim.query.filter_by(item_id=item.id, claimant_id=user.id).first()
        if not claim:
            abort(403)
        other_id = item.user_id
    other = db.get_or_404(User, other_id)
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if not body or len(body) > 2000:
            flash("Message must be between 1 and 2000 characters.", "error")
        else:
            db.session.add(Message(item_id=item.id, sender_id=user.id, recipient_id=other.id, body=body))
            create_notification(other.id, "New message", f"You have a new message about '{item.title}'.", url_for("item_messages", item_id=item.id, **({"with": user.id} if other.id == item.user_id else {})))
            db.session.commit()
            return redirect(url_for("item_messages", item_id=item.id, **({"with": other.id} if user.id == item.user_id else {})))
    conversation = Message.query.filter_by(item_id=item.id).filter(
        db.or_(db.and_(Message.sender_id == user.id, Message.recipient_id == other.id),
               db.and_(Message.sender_id == other.id, Message.recipient_id == user.id))
    ).order_by(Message.created_at.asc()).all()
    Message.query.filter_by(item_id=item.id, sender_id=other.id, recipient_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return render_template("conversation.html", item=item, other=other, conversation=conversation)

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user().role != "admin":
        abort(403)
    return render_template("admin.html", users=User.query.order_by(User.created_at.desc()).all(),
                           items=Item.query.order_by(Item.created_at.desc()).all(),
                           claims=Claim.query.order_by(Claim.created_at.desc()).all(),
                           stats={"users": User.query.count(), "items": Item.query.count(), "claims": Claim.query.count(),
                                  "open": Item.query.filter_by(status="open").count()})

@app.route("/admin/item/<int:item_id>/<action>", methods=["POST"])
@login_required
def admin_item_action(item_id, action):
    if current_user().role != "admin":
        abort(403)
    item = db.get_or_404(Item, item_id)
    if action not in {"hide", "restore"}:
        abort(400)
    item.status = "removed" if action == "hide" else "open"
    db.session.commit()
    flash(f"Listing {action}d.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/robots.txt")
def robots_txt():
    from flask import Response
    return Response("User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /dashboard\nDisallow: /messages\nDisallow: /notifications\nDisallow: /matches\nDisallow: /login\nDisallow: /register\n", mimetype="text/plain")

@app.errorhandler(400)
def bad_request(error):
    return render_template("400.html"), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template("405.html"), 405

@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template("413.html"), 413

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.exception("Unhandled application error")
    return render_template("500.html"), 500

@app.cli.command("create-admin")
def create_admin():
    """Create an admin account from environment variables ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD."""
    name = os.getenv("ADMIN_NAME", "Retrieve Admin")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        raise SystemExit("Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables first.")
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        user = User(name=name, email=email.lower(), password_hash=generate_password_hash(password), role="admin")
        db.session.add(user)
    else:
        user.role = "admin"
    db.session.commit()
    print(f"Admin ready: {email}")

@app.cli.command("init-db")
def init_db():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")

if __name__ == "__main__":
    app.run(debug=True)

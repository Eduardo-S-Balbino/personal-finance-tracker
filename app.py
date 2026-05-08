from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text
from datetime import datetime, date
from calendar import monthrange
from types import SimpleNamespace
from models import db, User, Transaction
import csv
import io
import os


def ensure_user_goal_column():
    inspector = inspect(db.engine)
    columns = [column["name"] for column in inspector.get_columns("user")]

    if "goal_percentage" not in columns:
        with db.engine.begin() as connection:
            connection.execute(
                text('ALTER TABLE "user" ADD COLUMN goal_percentage FLOAT DEFAULT 20')
            )


def build_effective_transactions(raw_transactions, target_month, target_year):
    effective_transactions = []

    for transaction in raw_transactions:
        if transaction.is_recurring and transaction.recurrence_type == "monthly":
            start_date = transaction.date

            if (start_date.year, start_date.month) <= (target_year, target_month):
                last_day_of_target_month = monthrange(target_year, target_month)[1]
                effective_day = min(start_date.day, last_day_of_target_month)

                effective_date = date(target_year, target_month, effective_day)

                effective_transaction = SimpleNamespace(
                    id=transaction.id,
                    title=transaction.title,
                    amount=transaction.amount,
                    type=transaction.type,
                    category=transaction.category,
                    date=effective_date,
                    description=transaction.description,
                    is_recurring=transaction.is_recurring,
                    recurrence_type=transaction.recurrence_type,
                    user_id=transaction.user_id
                )

                effective_transactions.append(effective_transaction)
        else:
            if transaction.date.month == target_month and transaction.date.year == target_year:
                effective_transactions.append(transaction)

    effective_transactions.sort(key=lambda transaction: transaction.date, reverse=True)
    return effective_transactions


def get_filtered_transactions_for_user(user_id):
    current_date = datetime.today()

    selected_month = request.args.get("month", default=current_date.month, type=int)
    selected_year = request.args.get("year", default=current_date.year, type=int)
    selected_type = request.args.get("type", default="")
    selected_category = request.args.get("category", default="")
    search_title = request.args.get("search", default="").strip()

    raw_transactions = Transaction.query.filter_by(
        user_id=user_id
    ).order_by(Transaction.date.desc()).all()

    monthly_transactions = build_effective_transactions(
        raw_transactions,
        selected_month,
        selected_year
    )

    filtered_transactions = monthly_transactions

    if selected_type:
        filtered_transactions = [
            transaction for transaction in filtered_transactions
            if transaction.type == selected_type
        ]

    if selected_category:
        filtered_transactions = [
            transaction for transaction in filtered_transactions
            if transaction.category == selected_category
        ]

    if search_title:
        search_lower = search_title.lower()
        filtered_transactions = [
            transaction for transaction in filtered_transactions
            if search_lower in transaction.title.lower()
        ]

    available_categories = sorted(
        list({transaction.category for transaction in monthly_transactions})
    )

    return {
        "transactions": filtered_transactions,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "selected_type": selected_type,
        "selected_category": selected_category,
        "search_title": search_title,
        "available_categories": available_categories
    }


def create_demo_account():
    demo_email = "demo@finance.com"
    demo_username = "Demo User"
    demo_password = "demo123"

    demo_user = User.query.filter_by(email=demo_email).first()

    if not demo_user:
        demo_user = User(
            username=demo_username,
            email=demo_email,
            password=generate_password_hash(demo_password),
            goal_percentage=20
        )

        db.session.add(demo_user)
        db.session.commit()

    existing_transactions = Transaction.query.filter_by(user_id=demo_user.id).first()

    if not existing_transactions:
        today = date.today()

        demo_transactions = [
            Transaction(
                title="Salário",
                amount=3500.00,
                type="receita",
                category="Trabalho",
                date=date(today.year, today.month, 5),
                description="Receita mensal principal",
                is_recurring=True,
                recurrence_type="monthly",
                user_id=demo_user.id
            ),
            Transaction(
                title="Aluguel",
                amount=1200.00,
                type="despesa",
                category="Moradia",
                date=date(today.year, today.month, 10),
                description="Despesa mensal recorrente",
                is_recurring=True,
                recurrence_type="monthly",
                user_id=demo_user.id
            ),
            Transaction(
                title="Internet",
                amount=120.00,
                type="despesa",
                category="Serviços",
                date=date(today.year, today.month, 12),
                description="Internet residencial",
                is_recurring=True,
                recurrence_type="monthly",
                user_id=demo_user.id
            ),
            Transaction(
                title="Supermercado",
                amount=450.00,
                type="despesa",
                category="Alimentação",
                date=today,
                description="Compra mensal",
                is_recurring=False,
                recurrence_type=None,
                user_id=demo_user.id
            ),
            Transaction(
                title="Freelance",
                amount=800.00,
                type="receita",
                category="Extra",
                date=today,
                description="Projeto freelance",
                is_recurring=False,
                recurrence_type=None,
                user_id=demo_user.id
            )
        ]

        db.session.add_all(demo_transactions)
        db.session.commit()

    return demo_user


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    app.secret_key = os.environ.get("SECRET_KEY", "minha_chave_secreta")
    app.url_map.strict_slashes = False

    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    def get_current_user():
        if "user_id" not in session:
            return None

        user = User.query.get(session["user_id"])

        if not user:
            session.clear()
            flash("Sua sessão expirou. Faça login novamente.")
            return None

        return user

    @app.route("/api/health")
    @app.route("/api/health/")
    def api_health():
        return jsonify({
            "status": "ok",
            "message": "API is running",
            "project": "Personal Finance Tracker"
        }), 200



    @app.route("/api/demo-login", methods=["GET", "POST"])
    @app.route("/api/demo-login/", methods=["GET", "POST"])
    def api_demo_login():
        demo_user = create_demo_account()

        session["user_id"] = demo_user.id
        session["username"] = demo_user.username

        return jsonify({
            "status": "ok",
            "message": "Demo login successful",
            "user": {
                "id": demo_user.id,
                "username": demo_user.username,
                "email": demo_user.email
            }
        }), 200

    @app.route("/api/dashboard")
    @app.route("/api/dashboard/")
    def api_dashboard():
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                "status": "error",
                "message": "Authentication required"
            }), 401

        current_date = datetime.today()

        selected_month = request.args.get("month", default=current_date.month, type=int)
        selected_year = request.args.get("year", default=current_date.year, type=int)
        selected_type = request.args.get("type", default="")
        selected_category = request.args.get("category", default="")

        raw_transactions = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(Transaction.date.desc()).all()

        monthly_transactions = build_effective_transactions(
            raw_transactions,
            selected_month,
            selected_year
        )

        filtered_transactions = monthly_transactions

        if selected_type:
            filtered_transactions = [
                transaction for transaction in filtered_transactions
                if transaction.type == selected_type
            ]

        if selected_category:
            filtered_transactions = [
                transaction for transaction in filtered_transactions
                if transaction.category == selected_category
            ]

        total_income = sum(
            transaction.amount for transaction in filtered_transactions
            if transaction.type == "receita"
        )

        total_expense = sum(
            transaction.amount for transaction in filtered_transactions
            if transaction.type == "despesa"
        )

        balance = total_income - total_expense

        savings_rate = 0
        if total_income > 0:
            savings_rate = ((balance / total_income) * 100)

        goal_percentage = current_user.goal_percentage or 20

        goal_progress = 0
        if savings_rate > 0:
            goal_progress = (savings_rate / goal_percentage) * 100

        if goal_progress > 100:
            goal_progress = 100

        recent_transactions = filtered_transactions[:5]

        expense_by_category = {}

        for transaction in filtered_transactions:
            if transaction.type == "despesa":
                category = transaction.category
                expense_by_category[category] = expense_by_category.get(category, 0) + transaction.amount

        chart_labels = list(expense_by_category.keys())
        chart_values = list(expense_by_category.values())

        top_category = None
        if expense_by_category:
            top_category = max(expense_by_category, key=expense_by_category.get)

        monthly_labels = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]

        monthly_income_values = []
        monthly_expense_values = []

        for month in range(1, 13):
            month_transactions = build_effective_transactions(
                raw_transactions,
                month,
                selected_year
            )

            month_income = sum(
                transaction.amount for transaction in month_transactions
                if transaction.type == "receita"
            )

            month_expense = sum(
                transaction.amount for transaction in month_transactions
                if transaction.type == "despesa"
            )

            monthly_income_values.append(month_income)
            monthly_expense_values.append(month_expense)

        alerts = []

        current_month_index = selected_month - 1
        current_expense = monthly_expense_values[current_month_index]

        previous_expense = 0
        if current_month_index > 0:
            previous_expense = monthly_expense_values[current_month_index - 1]

        if total_expense > total_income:
            alerts.append("Você está gastando mais do que ganha neste mês.")

        if previous_expense > 0 and current_expense > previous_expense:
            increase = ((current_expense - previous_expense) / previous_expense) * 100
            alerts.append(f"Seus gastos aumentaram {increase:.1f}% em relação ao mês anterior.")

        if top_category and total_expense > 0:
            top_value = max(chart_values) if chart_values else 0
            percentage = (top_value / total_expense) * 100

            if percentage > 50:
                alerts.append(f"A categoria '{top_category}' representa {percentage:.1f}% dos seus gastos.")

        available_categories = sorted(
            list({transaction.category for transaction in monthly_transactions})
        )

        serialized_recent_transactions = []
        for transaction in recent_transactions:
            serialized_recent_transactions.append({
                "id": transaction.id,
                "title": transaction.title,
                "amount": transaction.amount,
                "type": transaction.type,
                "category": transaction.category,
                "date": transaction.date.isoformat(),
                "description": transaction.description if transaction.description else "",
                "is_recurring": transaction.is_recurring,
                "recurrence_type": transaction.recurrence_type
            })

        return jsonify({
            "status": "ok",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            },
            "filters": {
                "selected_month": selected_month,
                "selected_year": selected_year,
                "selected_type": selected_type,
                "selected_category": selected_category,
                "available_categories": available_categories
            },
            "summary": {
                "total_income": round(total_income, 2),
                "total_expense": round(total_expense, 2),
                "balance": round(balance, 2),
                "savings_rate": round(savings_rate, 1),
                "goal_percentage": goal_percentage,
                "goal_progress": round(goal_progress, 1),
                "top_category": top_category
            },
            "alerts": alerts,
            "recent_transactions": serialized_recent_transactions,
            "charts": {
                "expense_by_category": {
                    "labels": chart_labels,
                    "values": chart_values
                },
                "monthly_evolution": {
                    "labels": monthly_labels,
                    "income_values": monthly_income_values,
                    "expense_values": monthly_expense_values
                }
            }
        }), 200

    @app.route("/api/transactions")
    @app.route("/api/transactions/")
    def api_transactions():
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                "status": "error",
                "message": "Authentication required"
            }), 401

        data = get_filtered_transactions_for_user(current_user.id)
        all_transactions = data["transactions"]

        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        if per_page < 1:
            per_page = 10

        if per_page > 50:
            per_page = 50

        total_transactions = len(all_transactions)
        total_pages = (total_transactions + per_page - 1) // per_page

        if total_pages == 0:
            total_pages = 1

        if page < 1:
            page = 1

        if page > total_pages:
            page = total_pages

        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        paginated_transactions = all_transactions[start_index:end_index]

        serialized_transactions = []
        for transaction in paginated_transactions:
            serialized_transactions.append({
                "id": transaction.id,
                "title": transaction.title,
                "amount": transaction.amount,
                "type": transaction.type,
                "category": transaction.category,
                "date": transaction.date.isoformat(),
                "description": transaction.description if transaction.description else "",
                "is_recurring": transaction.is_recurring,
                "recurrence_type": transaction.recurrence_type
            })

        return jsonify({
            "status": "ok",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            },
            "filters": {
                "selected_month": data["selected_month"],
                "selected_year": data["selected_year"],
                "selected_type": data["selected_type"],
                "selected_category": data["selected_category"],
                "search_title": data["search_title"],
                "available_categories": data["available_categories"]
            },
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "total_transactions": total_transactions
            },
            "transactions": serialized_transactions
        }), 200



    @app.route("/api/transactions/<int:transaction_id>", methods=["PUT"])
    @app.route("/api/transactions/<int:transaction_id>/", methods=["PUT"])
    def api_update_transaction(transaction_id):
        current_user = get_current_user()

        if not current_user:
            return jsonify({
                "status": "error",
                "message": "Authentication required"
            }), 401

        transaction = Transaction.query.get(transaction_id)

        if not transaction:
            return jsonify({
                "status": "error",
                "message": "Transaction not found"
            }), 404

        if transaction.user_id != current_user.id:
            return jsonify({
                "status": "error",
                "message": "You do not have permission to update this transaction"
            }), 403

        payload = request.get_json(silent=True)

        if not payload:
            return jsonify({
                "status": "error",
                "message": "JSON body is required"
            }), 400

        if "title" in payload:
            title = str(payload.get("title", "")).strip()

            if not title:
                return jsonify({
                    "status": "error",
                    "message": "Title cannot be empty"
                }), 400

            transaction.title = title

        if "amount" in payload:
            amount = payload.get("amount")

            try:
                amount = float(amount)
            except (TypeError, ValueError):
                return jsonify({
                    "status": "error",
                    "message": "Amount must be a valid number"
                }), 400

            if amount <= 0:
                return jsonify({
                    "status": "error",
                    "message": "Amount must be greater than zero"
                }), 400

            transaction.amount = amount

        if "type" in payload:
            type_ = str(payload.get("type", "")).strip().lower()

            if type_ not in ["receita", "despesa"]:
                return jsonify({
                    "status": "error",
                    "message": "Type must be 'receita' or 'despesa'"
                }), 400

            transaction.type = type_

        if "category" in payload:
            category = str(payload.get("category", "")).strip()

            if not category:
                return jsonify({
                    "status": "error",
                    "message": "Category cannot be empty"
                }), 400

            transaction.category = category

        if "date" in payload:
            date_str = str(payload.get("date", "")).strip()

            try:
                transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Date must be in YYYY-MM-DD format"
                }), 400

            transaction.date = transaction_date

        if "description" in payload:
            transaction.description = str(payload.get("description", "")).strip()

        if "recurrence" in payload:
            recurrence = str(payload.get("recurrence", "once")).strip().lower()
            transaction.is_recurring = recurrence == "monthly"
            transaction.recurrence_type = "monthly" if transaction.is_recurring else None

        db.session.commit()

        return jsonify({
            "status": "ok",
            "message": "Transaction updated successfully",
            "transaction": {
                "id": transaction.id,
                "title": transaction.title,
                "amount": transaction.amount,
                "type": transaction.type,
                "category": transaction.category,
                "date": transaction.date.isoformat(),
                "description": transaction.description if transaction.description else "",
                "is_recurring": transaction.is_recurring,
                "recurrence_type": transaction.recurrence_type
            }
        }), 200


    @app.route("/")
    def home():
        current_user = get_current_user()

        if current_user:
            return redirect(url_for("dashboard"))

        return redirect(url_for("login"))

    @app.route("/demo-login")
    @app.route("/demo-login/")
    def demo_login():
        demo_user = create_demo_account()

        session["user_id"] = demo_user.id
        session["username"] = demo_user.username

        flash("Você entrou como usuário demo.")
        return redirect(url_for("dashboard"))

    @app.route("/login", methods=["GET", "POST"])
    @app.route("/login/", methods=["GET", "POST"])
    def login():
        current_user = get_current_user()

        if current_user:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                flash("Preencha todos os campos.")
                return redirect(url_for("login"))

            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["username"] = user.username
                flash("Login realizado com sucesso!")
                return redirect(url_for("dashboard"))

            flash("E-mail ou senha inválidos.")
            return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    @app.route("/register/", methods=["GET", "POST"])
    def register():
        current_user = get_current_user()

        if current_user:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not username or not email or not password or not confirm_password:
                flash("Preencha todos os campos.")
                return redirect(url_for("register"))

            if password != confirm_password:
                flash("As senhas não coincidem.")
                return redirect(url_for("register"))

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Este nome de usuário já está em uso.")
                return redirect(url_for("register"))

            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash("Este e-mail já está cadastrado.")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                goal_percentage=20
            )

            db.session.add(new_user)
            db.session.commit()

            flash("Conta criada com sucesso!")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/update-goal", methods=["POST"])
    @app.route("/update-goal/", methods=["POST"])
    def update_goal():
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        goal_percentage = request.form.get("goal_percentage", type=float)

        if goal_percentage not in [10.0, 20.0, 30.0]:
            flash("Escolha uma meta válida.")
            return redirect(url_for("dashboard"))

        current_user.goal_percentage = goal_percentage

        db.session.commit()

        flash("Meta financeira atualizada com sucesso!")
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @app.route("/dashboard/")
    def dashboard():
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        current_date = datetime.today()

        selected_month = request.args.get("month", default=current_date.month, type=int)
        selected_year = request.args.get("year", default=current_date.year, type=int)
        selected_type = request.args.get("type", default="")
        selected_category = request.args.get("category", default="")

        raw_transactions = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(Transaction.date.desc()).all()

        monthly_transactions = build_effective_transactions(
            raw_transactions,
            selected_month,
            selected_year
        )

        filtered_transactions = monthly_transactions

        if selected_type:
            filtered_transactions = [
                transaction for transaction in filtered_transactions
                if transaction.type == selected_type
            ]

        if selected_category:
            filtered_transactions = [
                transaction for transaction in filtered_transactions
                if transaction.category == selected_category
            ]

        total_income = sum(
            transaction.amount for transaction in filtered_transactions
            if transaction.type == "receita"
        )

        total_expense = sum(
            transaction.amount for transaction in filtered_transactions
            if transaction.type == "despesa"
        )

        balance = total_income - total_expense

        savings_rate = 0
        if total_income > 0:
            savings_rate = ((balance / total_income) * 100)

        goal_percentage = current_user.goal_percentage or 20

        goal_progress = 0
        if savings_rate > 0:
            goal_progress = (savings_rate / goal_percentage) * 100

        if goal_progress > 100:
            goal_progress = 100

        recent_transactions = filtered_transactions[:5]

        expense_by_category = {}

        for transaction in filtered_transactions:
            if transaction.type == "despesa":
                category = transaction.category
                expense_by_category[category] = expense_by_category.get(category, 0) + transaction.amount

        chart_labels = list(expense_by_category.keys())
        chart_values = list(expense_by_category.values())

        top_category = None
        if expense_by_category:
            top_category = max(expense_by_category, key=expense_by_category.get)

        monthly_labels = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]

        monthly_income_values = []
        monthly_expense_values = []

        for month in range(1, 13):
            month_transactions = build_effective_transactions(
                raw_transactions,
                month,
                selected_year
            )

            month_income = sum(
                transaction.amount for transaction in month_transactions
                if transaction.type == "receita"
            )

            month_expense = sum(
                transaction.amount for transaction in month_transactions
                if transaction.type == "despesa"
            )

            monthly_income_values.append(month_income)
            monthly_expense_values.append(month_expense)

        alerts = []

        current_month_index = selected_month - 1
        current_expense = monthly_expense_values[current_month_index]

        previous_expense = 0
        if current_month_index > 0:
            previous_expense = monthly_expense_values[current_month_index - 1]

        if total_expense > total_income:
            alerts.append("Você está gastando mais do que ganha neste mês.")

        if previous_expense > 0 and current_expense > previous_expense:
            increase = ((current_expense - previous_expense) / previous_expense) * 100
            alerts.append(f"Seus gastos aumentaram {increase:.1f}% em relação ao mês anterior.")

        if top_category and total_expense > 0:
            top_value = max(chart_values) if chart_values else 0
            percentage = (top_value / total_expense) * 100

            if percentage > 50:
                alerts.append(f"A categoria '{top_category}' representa {percentage:.1f}% dos seus gastos.")

        available_categories = sorted(
            list({transaction.category for transaction in monthly_transactions})
        )

        return render_template(
            "dashboard.html",
            username=current_user.username,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            savings_rate=round(savings_rate, 1),
            goal_percentage=goal_percentage,
            goal_progress=round(goal_progress, 1),
            top_category=top_category,
            alerts=alerts,
            recent_transactions=recent_transactions,
            selected_month=selected_month,
            selected_year=selected_year,
            selected_type=selected_type,
            selected_category=selected_category,
            available_categories=available_categories,
            chart_labels=chart_labels,
            chart_values=chart_values,
            monthly_labels=monthly_labels,
            monthly_income_values=monthly_income_values,
            monthly_expense_values=monthly_expense_values
        )

    @app.route("/add_transaction", methods=["GET", "POST"])
    @app.route("/add_transaction/", methods=["GET", "POST"])
    def add_transaction():
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        if request.method == "POST":
            title = request.form.get("title")
            amount = request.form.get("amount")
            type_ = request.form.get("type")
            category = request.form.get("category")
            date_str = request.form.get("date")
            description = request.form.get("description")
            recurrence = request.form.get("recurrence")

            if not title or not amount or not type_ or not category or not date_str or not recurrence:
                flash("Preencha todos os campos obrigatórios.")
                return redirect(url_for("add_transaction"))

            try:
                amount = float(amount)
            except ValueError:
                flash("Digite um valor numérico válido.")
                return redirect(url_for("add_transaction"))

            if amount <= 0:
                flash("O valor deve ser maior que zero.")
                return redirect(url_for("add_transaction"))

            try:
                transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Digite uma data válida.")
                return redirect(url_for("add_transaction"))

            is_recurring = recurrence == "monthly"
            recurrence_type = "monthly" if recurrence == "monthly" else None

            new_transaction = Transaction(
                title=title,
                amount=amount,
                type=type_,
                category=category,
                date=transaction_date,
                description=description,
                is_recurring=is_recurring,
                recurrence_type=recurrence_type,
                user_id=current_user.id
            )

            db.session.add(new_transaction)
            db.session.commit()

            flash("Transação adicionada com sucesso!")
            return redirect(url_for("transactions"))

        return render_template("add_transaction.html")

    @app.route("/transactions")
    @app.route("/transactions/")
    def transactions():
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        data = get_filtered_transactions_for_user(current_user.id)
        all_transactions = data["transactions"]

        page = request.args.get("page", default=1, type=int)
        per_page = 5

        total_transactions = len(all_transactions)
        total_pages = (total_transactions + per_page - 1) // per_page

        if total_pages == 0:
            total_pages = 1

        if page < 1:
            page = 1

        if page > total_pages:
            page = total_pages

        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        paginated_transactions = all_transactions[start_index:end_index]

        return render_template(
            "transactions.html",
            transactions=paginated_transactions,
            selected_month=data["selected_month"],
            selected_year=data["selected_year"],
            selected_type=data["selected_type"],
            selected_category=data["selected_category"],
            available_categories=data["available_categories"],
            search_title=data["search_title"],
            page=page,
            total_pages=total_pages
        )

    @app.route("/export_transactions_csv")
    @app.route("/export_transactions_csv/")
    def export_transactions_csv():
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        data = get_filtered_transactions_for_user(current_user.id)
        transactions = data["transactions"]

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Titulo",
            "Valor",
            "Tipo",
            "Categoria",
            "Recorrencia",
            "Data",
            "Descricao"
        ])

        for transaction in transactions:
            recurrence_label = "Mensal" if transaction.is_recurring and transaction.recurrence_type == "monthly" else "Única"

            writer.writerow([
                transaction.title,
                f"{transaction.amount:.2f}",
                transaction.type,
                transaction.category,
                recurrence_label,
                transaction.date.strftime("%d/%m/%Y"),
                transaction.description if transaction.description else ""
            ])

        csv_content = output.getvalue()
        output.close()

        filename = f"transacoes_{data['selected_month']:02d}_{data['selected_year']}.csv"

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @app.route("/edit_transaction/<int:transaction_id>", methods=["GET", "POST"])
    @app.route("/edit_transaction/<int:transaction_id>/", methods=["GET", "POST"])
    def edit_transaction(transaction_id):
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        transaction = Transaction.query.get_or_404(transaction_id)

        if transaction.user_id != current_user.id:
            flash("Você não tem permissão para editar esta transação.")
            return redirect(url_for("transactions"))

        if request.method == "POST":
            title = request.form.get("title")
            amount = request.form.get("amount")
            type_ = request.form.get("type")
            category = request.form.get("category")
            date_str = request.form.get("date")
            description = request.form.get("description")
            recurrence = request.form.get("recurrence")

            if not title or not amount or not type_ or not category or not date_str or not recurrence:
                flash("Preencha todos os campos obrigatórios.")
                return redirect(url_for("edit_transaction", transaction_id=transaction.id))

            try:
                amount = float(amount)
            except ValueError:
                flash("Digite um valor numérico válido.")
                return redirect(url_for("edit_transaction", transaction_id=transaction.id))

            if amount <= 0:
                flash("O valor deve ser maior que zero.")
                return redirect(url_for("edit_transaction", transaction_id=transaction.id))

            try:
                transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Digite uma data válida.")
                return redirect(url_for("edit_transaction", transaction_id=transaction.id))

            transaction.title = title
            transaction.amount = amount
            transaction.type = type_
            transaction.category = category
            transaction.date = transaction_date
            transaction.description = description
            transaction.is_recurring = recurrence == "monthly"
            transaction.recurrence_type = "monthly" if recurrence == "monthly" else None

            db.session.commit()

            flash("Transação atualizada com sucesso!")
            return redirect(url_for("transactions"))

        return render_template("edit_transaction.html", transaction=transaction)

    @app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
    @app.route("/delete_transaction/<int:transaction_id>/", methods=["POST"])
    def delete_transaction(transaction_id):
        current_user = get_current_user()

        if not current_user:
            return redirect(url_for("login"))

        transaction = Transaction.query.get_or_404(transaction_id)

        if transaction.user_id != current_user.id:
            flash("Você não tem permissão para excluir esta transação.")
            return redirect(url_for("transactions"))

        db.session.delete(transaction)
        db.session.commit()

        flash("Transação excluída com sucesso!")
        return redirect(url_for("transactions"))

    @app.route("/logout")
    @app.route("/logout/")
    def logout():
        session.clear()
        flash("Você saiu da conta com sucesso.")
        return redirect(url_for("login"))

    with app.app_context():
        db.create_all()
        ensure_user_goal_column()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
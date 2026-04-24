from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from calendar import monthrange
from types import SimpleNamespace
import csv
import io
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "minha_chave_secreta")

database_url = os.environ.get("DATABASE_URL")

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


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


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
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

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Conta criada com sucesso!")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@app.route("/dashboard/")
def dashboard():
    if "user_id" not in session:
        flash("Faça login para acessar o dashboard.")
        return redirect(url_for("login"))

    current_date = datetime.today()

    selected_month = request.args.get("month", default=current_date.month, type=int)
    selected_year = request.args.get("year", default=current_date.year, type=int)
    selected_type = request.args.get("type", default="")
    selected_category = request.args.get("category", default="")

    raw_transactions = Transaction.query.filter_by(
        user_id=session["user_id"]
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
    recent_transactions = filtered_transactions[:5]

    expense_by_category = {}

    for transaction in filtered_transactions:
        if transaction.type == "despesa":
            category = transaction.category
            expense_by_category[category] = expense_by_category.get(category, 0) + transaction.amount

    chart_labels = list(expense_by_category.keys())
    chart_values = list(expense_by_category.values())

    available_categories = sorted(
        list({transaction.category for transaction in monthly_transactions})
    )

    return render_template(
        "dashboard.html",
        username=session["username"],
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        recent_transactions=recent_transactions,
        selected_month=selected_month,
        selected_year=selected_year,
        selected_type=selected_type,
        selected_category=selected_category,
        available_categories=available_categories,
        chart_labels=chart_labels,
        chart_values=chart_values
    )


@app.route("/add_transaction", methods=["GET", "POST"])
@app.route("/add_transaction/", methods=["GET", "POST"])
def add_transaction():
    if "user_id" not in session:
        flash("Faça login para adicionar uma transação.")
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
            user_id=session["user_id"]
        )

        db.session.add(new_transaction)
        db.session.commit()

        flash("Transação adicionada com sucesso!")
        return redirect(url_for("transactions"))

    return render_template("add_transaction.html")


@app.route("/transactions")
@app.route("/transactions/")
def transactions():
    if "user_id" not in session:
        flash("Faça login para visualizar suas transações.")
        return redirect(url_for("login"))

    data = get_filtered_transactions_for_user(session["user_id"])
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
    if "user_id" not in session:
        flash("Faça login para exportar suas transações.")
        return redirect(url_for("login"))

    data = get_filtered_transactions_for_user(session["user_id"])
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
    if "user_id" not in session:
        flash("Faça login para editar uma transação.")
        return redirect(url_for("login"))

    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.user_id != session["user_id"]:
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
    if "user_id" not in session:
        flash("Faça login para excluir uma transação.")
        return redirect(url_for("login"))

    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.user_id != session["user_id"]:
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


if __name__ == "__main__":
    app.run(debug=True)
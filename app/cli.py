from typer import Typer
from app.library import library_app
from app.books import books_app
from app.members import members_app

app = Typer(name="Library Management")

app.add_typer(library_app, name="lib")

app.add_typer(members_app, name="members")

app.add_typer(books_app, name="books")

from dataclasses import dataclass
from typing import List
from decimal import Decimal
from typer import Typer
from fuzzywuzzy import fuzz
from app.books import Book
from app import state
from app.errors import (
    EntityNotFound,
)
from app.members import Member
from app.utils import read_json


@dataclass
class Library:
    books: List[Book]
    late_fee_percentage: Decimal

    def get_book(self, book_title: str) -> Book:
        for book in self.books:
            if book.title == book_title:
                return book

        raise EntityNotFound(f"book `{book_title}` not found")

    def search_book_by_title(self, book_title: str) -> Book:
        for book in self.books:
            if fuzz.partial_ratio(book_title, book.title) > 95:
                return book

    def add_book(self, book: Book):
        self.books.append(book)

    def remove_book(self, book: Book):
        self.books.remove(book)

    def display_all_books(self) -> List[Book]:
        return self.books

    def search_books_by_author(self, author_name) -> List[Book]:
        books = []
        for book in self.books:
            for author in book.authors:
                if fuzz.partial_ratio(author, author_name) > 95:
                    books.append(book)
                    break
        return books


class LibrarySystem:
    def __init__(self, library: Library, members: List[Member]):
        self.library = library
        self.members = members

    def add_member(self, member: Member):
        member.join_library(self)
        self.members.append(member)

    def remove_member(self, member_name: str):
        for member in self.members:
            if member.name == member_name:
                return self._remove_member(member)
        raise EntityNotFound(f"member with name `{member_name}` not found")

    def _remove_member(self, member: Member):
        self.members.remove(member)
        member.leave_library()

    def get_member(self, member_name: str) -> Member:
        for member in self.members:
            if member.name == member_name:
                return member
        raise EntityNotFound(f"Member with name `{member_name}` not found")

    def display_all_members(self) -> List[Member]:
        return self.members

    def display_all_library_books(self) -> List[Book]:
        return self.library.books


library_app = Typer()


@library_app.command("create")
def create(path: str, late_fee: float):
    with open(path, "r") as fd:
        books = read_json(fd)

    lib = LibrarySystem(
        library=Library(books, late_fee_percentage=Decimal(late_fee)), members=[]
    )
    state.save(lib)
    print("Loaded")


@library_app.command("search")
def search(author_name: str):
    lib: LibrarySystem = state.load()

    for result in [
        lib.library.search_books_by_author(author_name),
        lib.library.search_book_by_title(author_name),
    ]:
        if result:
            print(result)
    state.save(lib)

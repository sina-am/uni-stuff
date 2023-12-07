from dataclasses import dataclass
import datetime
from typing import Dict, List
from decimal import Decimal
from typer import Typer

from app.books import Book, EditionNo

from app.errors import (
    EntityNotFound,
    LowBalance,
    MyException,
    NullMember,
    ToManyBorrowedBook,
    EntityExists,
)
from app import state

PENALTY_DUE = datetime.timedelta(seconds=30)


@dataclass
class Member:
    name: str
    borrowed_books: Dict[Book, EditionNo]
    return_due_dates: Dict[Book, datetime.datetime]
    balance: Decimal

    _joined_library = None

    def _borrow_book(self, book: Book, edition_no: EditionNo):
        book.remove_edition(edition_no)
        self.borrowed_books[book] = edition_no
        self.return_due_dates[book] = datetime.datetime.now() + PENALTY_DUE

    def _check_borrow_limit(self) -> bool:
        return len(self.borrowed_books) >= 2

    def _get_rental_fee(self, book: Book):
        return book.rental_fee

    def _apply_rental_fee(self, book: Book):
        charge = self._get_rental_fee(book) + self._get_late_penalty(book)
        if charge > self.balance:
            raise LowBalance("you don't have enough credit")

        self.balance -= charge

    def borrow_book(self, book_title: str, edition_no: EditionNo):
        if not self._joined_library:
            raise NullMember("you're not a member of this library")

        if self._check_borrow_limit():
            raise ToManyBorrowedBook(
                f"you already borrowed {len(self.borrowed_books)} books"
            )

        book = self._joined_library.library.get_book(book_title)

        if book in self.borrowed_books:
            raise EntityExists("you already have this book")

        self._borrow_book(book, edition_no)

    def _get_late_penalty(self, book: Book) -> Decimal:
        remaining_days = self.remaining_due_days(book)
        if remaining_days.total_seconds() > 0:  # no late penalty
            return Decimal(0.0)
        return (
            self._joined_library.library.late_fee_percentage
            * (self._get_rental_fee(book) * abs(remaining_days.days))
            / Decimal(100.0)
        )

    def return_book(self, book: Book):
        self._apply_rental_fee(book)
        book.add_edition(self.borrowed_books[book])
        del self.borrowed_books[book]
        del self.return_due_dates[book]

    def join_library(self, library):
        self._joined_library = library

    def leave_library(self):
        self._joined_library = None

    def display_borrowed_books(self) -> List[Book]:
        return self.borrowed_books

    def charge_balance(self, amount: Decimal):
        self.balance += amount

    def remaining_due_days(self, book: Book) -> datetime.timedelta:
        if not self.return_due_dates.get(book):
            raise EntityNotFound(f"book `{book.title}` hasn't borrowed yet")
        return self.return_due_dates[book] - datetime.datetime.now()


class SpecialMember(Member):
    discount_rate: Decimal

    def apply_discount(self, discount_rate: Decimal):
        self.discount_rate = discount_rate

    def _get_rental_fee(self, book: Book):
        return book.rental_fee * self.discount_rate / Decimal(100.0)


members_app = Typer()


@members_app.command("add")
def add_member(name: str, balance: float):
    member = Member(
        name, borrowed_books={}, return_due_dates={}, balance=Decimal(balance)
    )
    lib = state.load()
    try:
        lib.add_member(member)
    except MyException as exc:
        print(str(exc))

    print(member)
    state.save(lib)


@members_app.command("remove")
def remove_member(name: str):
    lib = state.load()
    try:
        lib.remove_member(name)
    except MyException as exc:
        print(str(exc))
    state.save(lib)


@members_app.command("list")
def list_members():
    lib = state.load()
    for member in lib.display_all_members():
        print("Name:", member.name)
        print("Balance:", member.balance)
        print("")
    state.save(lib)


@members_app.command("show")
def show_member(member_name: str):
    lib = state.load()

    try:
        member = lib.get_member(member_name)
    except MyException as exc:
        print(str(exc))
    print("Name:", member.name)
    print("Balance:", member.balance)
    print("Borrowed Books")
    for book in member.borrowed_books:
        print("\tBook Title:", book.title)
        print(
            f"\tDue: ({(member.return_due_dates[book] - datetime.datetime.now()).days})",
        )

    state.save(lib)


@members_app.command("borrow")
def borrow_book(member_name: str, book_title: str, edition_no: EditionNo):
    lib = state.load()

    try:
        member = lib.get_member(member_name)
        member.borrow_book(book_title, edition_no)
    except MyException as exc:
        print(str(exc))
    state.save(lib)


@members_app.command("return")
def return_book(name: str, book_title: str, edition_no: EditionNo):
    lib = state.load()

    try:
        member = lib.get_member(name)
        book = lib.library.get_book(book_title)
        member.return_book(book)
    except MyException as exc:
        print(str(exc))

    state.save(lib)

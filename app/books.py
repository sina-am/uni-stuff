from dataclasses import dataclass
import datetime
from typing import Dict, Set
from decimal import Decimal
from typer import Typer
from app import state
from app.errors import EntityNotFound, OutOfStock


EditionNo = str


@dataclass
class Book:
    title: str
    authors: Set[str]
    published_year: int
    editions: Dict[EditionNo, int]  # number of stock per edition
    rental_fee: Decimal

    def __hash__(self) -> int:
        return hash(f"{self.title}{''.join(self.authors)}{self.published_year}")

    def display_info(self) -> str:
        return self.__repr__()

    def add_edition(self, edition_no: EditionNo):
        if not self.editions.get(edition_no):
            self.edit_edition[edition_no] = 1
            return

        self.editions[edition_no] += 1

    def remove_edition(self, edition_no: EditionNo):
        if self.editions.get(edition_no) is None:
            raise EntityNotFound(
                f"book `{self.title}` don't have {edition_no}th edition"
            )
        if self.editions[edition_no] == 0:
            raise OutOfStock(f"there're no stock left for `{self.title}`")

        self.editions[edition_no] -= 1

    def edit_edition(self, edition_no: EditionNo):
        return self.add_edition(edition_no)

    def calculate_rental_fee(self, rental_days: datetime.timedelta) -> Decimal:
        return self.rental_fee * rental_days.days

    def save_to_csv(self) -> str:
        ...

    def load_from_csv(self):
        ...


books_app = Typer()


@books_app.command("list")
def list_books():
    lib = state.load()
    for book in lib.display_all_library_books():
        print(book)
    state.save(lib)

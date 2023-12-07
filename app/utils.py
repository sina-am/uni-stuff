from app.library import Book
from typing import List
from decimal import Decimal
import csv
import json


def read_csv(fp) -> List[Book]:
    reader = csv.DictReader(fp)
    books = []
    for book in reader:
        books.append(
            Book(
                **{
                    "title": book["title"],
                    "authors": [x.strip() for x in book["author"].split(",")],
                    "published_year": book["published_year"],
                    "rental_fee": book["rental_fee"],
                }
            )
        )
        print(book)


def read_json(fp) -> List[Book]:
    books = []
    for book in json.load(fp, parse_float=Decimal):
        books.append(Book(**book))

    return books

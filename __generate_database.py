import database


def generate():
    # unique books
    books: list[dict] = []

    for book in database.books.values():
        book = dict(book)
        # changing the things that can differentiate different copies of the
        # same book
        del book['id']
        book['member'] = '0'

        if book not in books:
            books.append(book)

    db = {}

    book_id = 1
    for book in books:
        for i in range(10):
            book = dict(book)
            book['id'] = book_id
            db[book_id] = book
            book_id += 1

    print('books:', len(db))

    database.books = db

    database.update_database()


if __name__ == "__main__":
    generate()

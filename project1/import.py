import csv
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

BOOKS_FILE = 'books.csv'


def main():
    conn_args = {}
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        sys.exit("Environment variable not set: 'DATABASE_URL'")

    if 'pg8000' in db_url:
        conn_args = {'ssl': True}

    engine = create_engine(db_url, connect_args=conn_args)
    db = scoped_session(sessionmaker(bind=engine))

    csv_file = BOOKS_FILE
    if sys.argv[1:]:
        csv_file = sys.argv[0]

    print("Deleting old data...")
    db.execute("TRUNCATE TABLE books")
    db.commit()

    print(f"Loading books from '{csv_file}'")
    with open(csv_file) as fin:
        csv_reader = csv.DictReader(fin)
        for n, record in enumerate(csv_reader, start=1):
            db.execute("""INSERT INTO books (isbn, title, author, year)
                          VALUES (:isbn, :title, :author, :year)""",
                       record)
            print('.', end='', flush=True)
            if (n % 50) == 0:
                print(f" {n:4d}")
            # if n > 201:
            #     break

        print(f"Total loaded: {n}")

    db.commit()


if __name__ == "__main__":
    main()

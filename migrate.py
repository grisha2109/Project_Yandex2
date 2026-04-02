from sqlalchemy import text
from app import app, db

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE user ADD COLUMN password VARCHAR(100) NOT NULL DEFAULT ""'))
        conn.commit()
    print("Миграция выполнена!")
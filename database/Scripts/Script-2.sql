CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER,
    title TEXT NOT NULL,
    review_text TEXT NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    FOREIGN KEY (hero_id) REFERENCES heroes(id)
);
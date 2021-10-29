CREATE TABLE IF NOT EXISTS products (
    prod_id         BIGSERIAL NOT NULL PRIMARY KEY,
    prod_name       TEXT NOT NULL,
    prod_descr      TEXT,
    pic_id          BIGINT
                    REFERENCES pics(pic_id) ON DELETE CASCADE,
    prod_price      BIGINT NOT NULL,
    prod_instock    BIGINT NOT NULL,
    prod_created    TIMESTAMP NOT NULL DEFAULT NOW(),

    CHECK (CHAR_LENGTH(prod_name) > 0),
    CHECK (prod_price > 0),
    CHECK (prod_instock >= 0)
);

INSERT INTO products 
(
    prod_name,
    prod_descr,
    prod_price,
    prod_instock
)
VALUES
(
    'Compass', 
    'The wisest men only follow their own directions. Made in China.',
    1.98,
    5
),
(
    'Feather',
    'For practicing your calligraphy and taking notes of the groceries list',
    7.98,
    2
),
(
    'Thermometer',
    'An instrument made for measuring temperature. Keep away from children!',
    9.99,
    10
),
(
    'Candles',
    'Sometimes a dedicated artist will need to work into the night... too bad electricity was not yet invented! Contains 6 units.',
    1.49,
    87
),
(
    'Microscope',
    'I guess that was not even invented in the Renaissance, but certainly a Renaissance fellow could benefit from it',
    3.141596535,
    12
),
(
    'Compass', 
    'The wisest men only follow their own directions. Made in China.',
    1.98,
    5
),
(
    'Feather',
    'For practicing your calligraphy and taking notes of the groceries list',
    7.98,
    2
),
(
    'Thermometer',
    'An instrument made for measuring temperature. Keep away from children!',
    9.99,
    10
),
(
    'Candles',
    'Sometimes a dedicated artist will need to work into the night... too bad electricity was not yet invented! Contains 6 units.',
    1.49,
    87
),
(
    'Microscope',
    'I guess that was not even invented in the Renaissance, but certainly a Renaissance fellow could benefit from it',
    3.141596535,
    12
),
(
    'Compass', 
    'The wisest men only follow their own directions. Made in China.',
    1.98,
    5
),
(
    'Feather',
    'For practicing your calligraphy and taking notes of the groceries list',
    7.98,
    2
),
(
    'Thermometer',
    'An instrument made for measuring temperature. Keep away from children!',
    9.99,
    10
),
(
    'Candles',
    'Sometimes a dedicated artist will need to work into the night... too bad electricity was not yet invented! Contains 6 units.',
    1.49,
    87
),
(
    'Microscope',
    'I guess that was not even invented in the Renaissance, but certainly a Renaissance fellow could benefit from it',
    3.141596535,
    12
),
(
    'Compass', 
    'The wisest men only follow their own directions. Made in China.',
    1.98,
    5
),
(
    'Feather',
    'For practicing your calligraphy and taking notes of the groceries list',
    7.98,
    2
),
(
    'Thermometer',
    'An instrument made for measuring temperature. Keep away from children!',
    9.99,
    10
),
(
    'Candles',
    'Sometimes a dedicated artist will need to work into the night... too bad electricity was not yet invented! Contains 6 units.',
    1.49,
    87
),
(
    'Microscope',
    'I guess that was not even invented in the Renaissance, but certainly a Renaissance fellow could benefit from it',
    3.141596535,
    12
),
(
    'Compass', 
    'The wisest men only follow their own directions. Made in China.',
    1.98,
    5
),
(
    'Feather',
    'For practicing your calligraphy and taking notes of the groceries list',
    7.98,
    2
),
(
    'Thermometer',
    'An instrument made for measuring temperature. Keep away from children!',
    9.99,
    10
),
(
    'Candles',
    'Sometimes a dedicated artist will need to work into the night... too bad electricity was not yet invented! Contains 6 units.',
    1.49,
    87
),
(
    'Microscope',
    'I guess that was not even invented in the Renaissance, but certainly a Renaissance fellow could benefit from it',
    3.141596535,
    12
);
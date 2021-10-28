CREATE TABLE products (
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
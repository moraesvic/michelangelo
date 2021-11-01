CREATE TABLE IF NOT EXISTS pics (
    pic_id BIGSERIAL NOT NULL PRIMARY KEY,
	pic_md5 TEXT NOT NULL UNIQUE,
	pic_path TEXT NOT NULL,
    pic_created TIMESTAMP NOT NULL DEFAULT NOW(),
    pic_ref_count INT DEFAULT 1,

    -- MD5SUM must be equal to 32, or 16 bytes
    CHECK (CHAR_LENGTH(pic_md5) = 32),
    CHECK (CHAR_LENGTH(pic_path) > 0),
    CHECK (pic_ref_count > 0)
);

CREATE OR REPLACE FUNCTION fn_pic_decrease_ref_count
(my_pic_id BIGINT)
RETURNS BIGINT
AS
$$
-- if the picture was non-existent before running this function, or the
-- execution of this command caused its deletion, will return True,
-- if picture still exists, will return False
BEGIN
    IF EXISTS (
        SELECT FROM pics
        WHERE
            pic_id = my_pic_id
            AND pic_ref_count = 1
        )
    THEN
            DELETE
            FROM pics
            WHERE pic_id = my_pic_id;
    ELSE
            UPDATE pics
            SET pic_ref_count = pic_ref_count - 1
            WHERE pic_id = my_pic_id;
    END IF ;

    RETURN
    (
        SELECT
        CASE
            WHEN NOT EXISTS(SELECT FROM pics WHERE pic_id = my_pic_id) THEN 1
            ELSE 0
        END as deleted
    );
END
$$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION fn_pic_upsert
(my_pic_path TEXT, my_pic_md5 TEXT)
RETURNS BIGINT
AS
$$
INSERT INTO pics
(
    pic_path,
    pic_md5
)
VALUES
(
    my_pic_path,
    my_pic_md5
)
ON CONFLICT(pic_md5) DO
    UPDATE
    SET
    pic_ref_count = pics.pic_ref_count + 1
RETURNING pic_id ;
$$
LANGUAGE SQL;
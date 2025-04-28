-- SELECT
--     *
-- FROM
--     unmatched_trade
-- WHERE
--     valid_to > 4;

SELECT
    ut.*
FROM
    unmatched_trade AS ut
JOIN
    trade AS t
ON
    t.trade_id = ut.trade_id
WHERE
    t.security_id = 1
AND
    t.book_id = 1
AND
    ut.valid_to = 4294967295
ORDER BY
    ut.valid_from
LIMIT
    1


   SELECT
    COUNT(s.id),
    generate_series::date,
    s.browser
   FROM (
    SELECT c.id, c.date_time, c.browser
    FROM
     shorturls_linkclick c
    INNER JOIN
     shorturls_link l ON c.link_id = l.id
    WHERE
     l.user_id = 1) s
   RIGHT JOIN
      (
       SELECT
         DATE('2012-02-02') + q.a as generate_series
        FROM
         generate_series(0,45,1) as q(a)
      ) g
ON g.generate_series = DATE(c.date_time)

   GROUP BY
    g.generate_series, s.browser
   ORDER BY
    g.generate_series;
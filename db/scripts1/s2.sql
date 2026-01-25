SELECT * FROM mtr.pl_def_defrtg; --11
SELECT * FROM mtr.pl_def_fmwt; --2
SELECT * FROM mtr.pl_def_opp_or_pct; --1
SELECT * FROM mtr.pl_def_opp_scposs; --10
SELECT * FROM mtr.pl_def_stop1 --3
ORDER BY game_date DESC;
SELECT * FROM mtr.pl_def_stop2; --7
SELECT * FROM mtr.pl_def_stop2fg; --4
SELECT * FROM mtr.pl_def_stop2ft; --6
SELECT * FROM mtr.pl_def_stop2to; --5
SELECT * FROM mtr.pl_def_stop_pct; --9
SELECT * FROM mtr.pl_def_stop; --8

 SELECT step_order, procedure_name
        FROM ctl.pipeline_steps
        WHERE is_active and procedure_name LIKE '%def%'
        ORDER BY step_order

SELECT table_schema,
       table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_name ILIKE '%def%' and table_schema = 'mtr'
ORDER BY table_schema, table_name;

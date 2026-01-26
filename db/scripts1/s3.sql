CALL mtr.rebuild_team_possessions('E2025')

CALL mtr.rebuild_lg_possessions('E2025')

CALL mtr.rebuild_team_def_rating('E2025')

CALL mtr.rebuild_team_off_rating('E2025')

CALL mtr.rebuild_team_offdef_rating('E2025')

SELECT * FROM mtr.team_def_rating
WHERE team_code = 'RED'
SELECT * FROM mtr.team_off_rating
WHERE team_code = 'RED'

SELECT * FROM mtr.lg_possessions
WHERE game_date= '2025-09-30'

SELECT AVG(poss_in_day) FROM mtr.team_possessions
WHERE game_date= '2025-09-30'




SELECT * FROM mtr.game_possessions
WHERE team_code = 'RED'

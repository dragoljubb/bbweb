CALL mtr.rebuild_game_poss('E2025') -
CALL mtr.rebuild_team_poss('E2025')
CALL mtr.rebuild_lg_poss('E2025')

CALL mtr.rebuild_player_cper('E2025')

CALL mtr.rebuild_pl_per_ponder('E2025')

SELECT * FROM mtr.player_cper
WHERE team_code = 'PAR' and player_code = '006760'


SELECT * FROM mtr.per_ponder
SELECT p.per_until_day, i.formatted_name, p.player_code, p.minutes_until_day,
ofr.offrtg_until_date, dfr.defrtg_until_date FROM mtr.vw_player_last_per p
INNER JOIN dwh.vw_players_by_season i
ON i.person_code = p.player_code
INNER JOIN mtr.vw_player_off_rtg ofr
ON ofr.player_code = p.player_code
INNER JOIN mtr.vw_player_def_rtg dfr
ON dfr.player_code = p.player_code
WHERE p.team_code = 'RED'
ORDER BY minutes_until_day desc


	SELECT * FROM mtr.team_per_params t
	WHERE t.team_code = 'RED'

SELECT * FROM mtr.vw_player_last_per p
INNER JOIN dwh.vw_players_by_season i
ON i.person_code = p.player_code
INNER JOIN mtr.vw_player_off_rtg ofr

ON ofr.player_code = p.player_code
WHERE p.team_code = 'RED'
ORDER BY minutes_until_day desc

SELECT * FROM mtr.pl_def_opp_or_pct
WHERE 004866

select * from mtr.player_per
WHERE player_code = '004866'
ORDER BY Game_date

SELECT * FROM mtr.vw_player_off_rtg
WHERE team_code = 'RED'


SELECT id, season_code, game_code, game_date, team_code, poss_in_day, poss_until_day, created, updated
	FROM mtr.team_possessions
	WHERE team_code = 'RED'
	ORDER BY game_date

	SELECT id, season_code, game_date, team_code, team_pace_in_day, team_pace_until_day, created_at, updated_at
	FROM mtr.team_pace
	ORDER BY game_date DESC


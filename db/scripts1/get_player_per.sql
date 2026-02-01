SELECT season_code, as_of_date, player_code, team_code, cper_until_day, minutes_until_day, per_ponder, per_value
	FROM mtr.vw_player_per_as_of_date

	WHERE player_code = '006760'
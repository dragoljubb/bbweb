CREATE OR REPLACE PROCEDURE mtr.rebuild_pl_off_rating(
    IN p_season_code text
)
LANGUAGE plpgsql
AS $BODY$
DECLARE
    v_step_start timestamptz;
    v_step_name  text;
BEGIN
    /*
    Napomena:
	- Svi ulazni parametri su KUMULATIVNI (sufiks *_until_day).
	- Ne koristi se dnevna logika niti window funkcije.
	- Procedura samo primenjuje formulu nad već sabranim vrednostima.
	*/
	
     ------------------------------------------------------------------
     -- 1. TEMP: Team Scoring Possessions (TeScPoss)
			/*
		TeScPoss (Team Scored Possessions) – broj napada koje je tim završio poenom
		Formula:
		TeScPoss = TeFGM
		          + [ 1 - (1 - TeFTM / TeFTA)^2 ] * TeFTA * 0.4
		Gde je:
		- TeFGM  : broj pogođenih šuteva iz igre (Field Goals Made)
		- TeFTM  : broj pogođenih slobodnih bacanja (Free Throws Made)
		- TeFTA  : broj pokušaja slobodnih bacanja (Free Throws Attempted)
		*/
    ------------------------------------------------------------------
	v_step_name := 'STEP 1: TeScPoss';
    v_step_start := clock_timestamp();
    DROP TABLE IF EXISTS tmp_sc_poss;
	CREATE TEMP TABLE tmp_sc_poss AS
    SELECT
        season_code,
        game_date,
        game_code,
        team_code,

        te_fg_made_until_day
        +
        CASE
            WHEN te_ft_att_until_day > 0 THEN
                (1 - POWER(
                    1 - te_ft_made_until_day::numeric / te_ft_att_until_day, 2
                ))
                * te_ft_att_until_day * 0.4
            ELSE 0
        END AS te_sc_poss_until

    FROM mtr.team_per_params
    WHERE season_code = p_season_code;

    RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
    ------------------------------------------------------------------
    -- 2. TEMP: Team Play Percentage (TePl%)
			/*
		TePl% (Team Points per Possession / Play Percentage)
		
		Formula:
		TePl% = TeScPoss / (TeFGA + 0.44 * TeFTA + TeTO)
		
		Gde je:
		- TeScPoss : broj napada završenih poenom (scoring possessions)
		- TeFGA    : pokušaji šuta iz igre (Field Goal Attempts)
		- TeFTA    : pokušaji slobodnih bacanja (Free Throw Attempts)
		- TeTO     : izgubljene lopte (Turnovers)
		*/
    ------------------------------------------------------------------
    v_step_name := 'STEP 2: TePl%';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_pct;
	CREATE TEMP TABLE tmp_pl_pct AS
    SELECT
        tpp.season_code,
        tpp.game_date,
        tpp.game_code,
        tpp.team_code,

        CASE
            WHEN (
                tpp.te_fg_att_until_day
              + 0.44 * tpp.te_ft_att_until_day
              + tpp.te_tov_until_day
            ) > 0
            THEN
                sc.te_sc_poss_until
                /
                (
                    tpp.te_fg_att_until_day
                  + 0.44 * tpp.te_ft_att_until_day
                  + tpp.te_tov_until_day
                )
            ELSE 0
        END AS te_pl_pct_until

    FROM mtr.team_per_params tpp
    JOIN tmp_sc_poss sc
      ON sc.season_code = tpp.season_code
     AND sc.game_code   = tpp.game_code
     AND sc.team_code   = tpp.team_code;

    RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
    ------------------------------------------------------------------
    -- 3. TEMP: Offensive Rebound Weight (TeORW)
		/*
	TeORW (Team Offensive Rebound Weight)
	Formula:
	TeORW =
	    ( (1 - TeOR%) * TePl% )
	    ---------------------------------------------
	    ( (1 - TeOR%) * TePl% + (1 - TePl%) * TeOR% )
	
	Gde je:
	- TeOR%  : procenat ofanzivnih skokova
	           TeOR% = TeORB / (TeORB + TeDRB)
	- TePl%  : points per possession / play percentage
	*/
    ------------------------------------------------------------------
   v_step_name := 'STEP 3: TeORW%';
   v_step_start := clock_timestamp();
   DROP TABLE IF EXISTS tmp_orw;
	CREATE TEMP TABLE tmp_orw AS
    SELECT
        tpp.season_code,
        tpp.game_date,
        tpp.game_code,
        tpp.team_code,

        CASE
            WHEN
                (tpp.te_off_rebounds_until_day + tpp.te_def_rebounds_until_day) > 0
                AND pl.te_pl_pct_until BETWEEN 0 AND 1
            THEN
                (
                    (1 - (
                        tpp.te_off_rebounds_until_day::numeric
                        /
                        (tpp.te_off_rebounds_until_day + tpp.te_def_rebounds_until_day)
                    ))
                    * pl.te_pl_pct_until
                )
                /
                (
                    (1 - (
                        tpp.te_off_rebounds_until_day::numeric
                        /
                        (tpp.te_off_rebounds_until_day + tpp.te_def_rebounds_until_day)
                    ))
                    * pl.te_pl_pct_until
                    +
                    (1 - pl.te_pl_pct_until)
                    * (
                        tpp.te_off_rebounds_until_day::numeric
                        /
                        (tpp.te_off_rebounds_until_day + tpp.te_def_rebounds_until_day)
                    )
                )
            ELSE 0
        END AS te_orw_until

    FROM mtr.team_per_params tpp
    JOIN tmp_pl_pct pl
      ON pl.season_code = tpp.season_code
     AND pl.game_code   = tpp.game_code
     AND pl.team_code   = tpp.team_code;
      RAISE NOTICE '% duration: % ms',
      v_step_name,
      ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
	    ------------------------------------------------------------------
	-- STEP 4: Team adjustment factor "a"
	--
	-- Formula:
	-- a = 1 - (TeOR / TeScPoss) * TeORW * TePl%
	------------------------------------------------------------------
	v_step_name := 'STEP 4: "a"';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_te_a;
	CREATE TEMP TABLE tmp_te_a AS
	SELECT
	    tpp.season_code,
	    tpp.game_date,
	    tpp.game_code,
	    tpp.team_code,
	
	    CASE
	        WHEN sc.te_sc_poss_until > 0
	        THEN
	            1
	            -
	            (
	                (tpp.te_off_rebounds_until_day::numeric
	                 / sc.te_sc_poss_until)
	                * orw.te_orw_until
	                * pl.te_pl_pct_until
	            )
	        ELSE 1
	    END AS te_a_until
	
	FROM mtr.team_per_params tpp
	JOIN tmp_sc_poss sc
	  ON sc.season_code = tpp.season_code
	 AND sc.game_code   = tpp.game_code
	 AND sc.team_code   = tpp.team_code
	JOIN tmp_orw orw
	  ON orw.season_code = tpp.season_code
	 AND orw.game_code   = tpp.game_code
	 AND orw.team_code   = tpp.team_code
	JOIN tmp_pl_pct pl
	  ON pl.season_code = tpp.season_code
	 AND pl.game_code   = tpp.game_code
	 AND pl.team_code   = tpp.team_code
	WHERE tpp.season_code = p_season_code;

    RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		
		    ------------------------------------------------------------------
		-- STEP 5: qAst (Assist Adjustment Factor)
		--
		-- Formula:
		-- qAst =
		-- (5 * MP / TeMP) * 1.14 * (TeAst - Ast) / TeFGM
		-- +
		-- (1 - 5 * MP / TeMP)
		-- * [ (TeAst / TeMP * MP * 5 - Ast)
		--     /
		--     (TeFGM / TeMP * MP * 5 - FGM) ]
		--
		-- Gde je:
		-- - MP     : player minutes (until)
		-- - Ast    : player assists (until)
		-- - FGM    : player field goals made (until)
		-- - TeMP   : team minutes (until)
		-- - TeAst  : team assists (until)
		-- - TeFGM  : team field goals made (until)
		--
		-- Napomena:
		-- - qAst se računa na PLAYER nivou uz TEAM kontekst.
		-- - Nema dnevnih vrednosti, AVG-a ni window funkcija.
		-- - Ograničeno na prosleđenu sezonu (p_season_code).
		------------------------------------------------------------------
		v_step_name := 'STEP 5: qAst';
        v_step_start := clock_timestamp();
		DROP TABLE IF EXISTS tmp_pl_q_ast;
		CREATE TEMP TABLE tmp_pl_q_ast AS
		SELECT
		    p.season_code,
		    p.game_date,
		    p.game_code,
		    p.team_code,
		    p.player_code,
		
		    CASE
		        WHEN
		            p.minutes_until_day > 0
		            AND t.te_mp_until_day > 0
		            AND t.te_fg_made_until_day > 0
		            AND NULLIF(
		                (t.te_fg_made_until_day::numeric / t.te_mp_until_day)
		                * p.minutes_until_day * 5
		                - p.fgm_until_day,
		                0
		            ) IS NOT NULL
		        THEN
		            (
		                (5 * p.minutes_until_day / t.te_mp_until_day)
		                * 1.14
		                * (
		                    (t.te_ast_until_day - p.ast_until_day)::numeric
		                    / NULLIF(t.te_fg_made_until_day, 0)
		                )
		            )
		            +
		            (
		                (1 - (5 * p.minutes_until_day / t.te_mp_until_day))
		                *
		                (
		                    (
		                        (t.te_ast_until_day::numeric / t.te_mp_until_day)
		                        * p.minutes_until_day * 5
		                        - p.ast_until_day
		                    )
		                    /
		                    NULLIF(
		                        (t.te_fg_made_until_day::numeric / t.te_mp_until_day)
		                        * p.minutes_until_day * 5
		                        - p.fgm_until_day,
		                        0
		                    )
		                )
		            )
		        ELSE 0
		    END AS q_ast_until
		
		FROM mtr.player_per_params p
		JOIN mtr.team_per_params t
		  ON t.season_code = p.season_code
		 AND t.game_code   = p.game_code
		 AND t.team_code   = p.team_code
		WHERE p.season_code = p_season_code;

		RAISE NOTICE '% duration: % ms',
    	v_step_name,
    	ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
	
	
			------------------------------------------------------------------
	-- STEP 6: PtsGen_FG (Points Generated from Field Goals)
	--
	-- Formula:
	-- PtsGen_FG =
	-- 2 * (FGM + 0.5 * 3PM) * (1 - 0.5 * ((Pts - FTM) / (2 * FGA)) * qAst)
	--
	-- Gde je:
	-- - FGM   : player field goals made (until)
	-- - 3PM   : player 3pt field goals made (until)
	-- - FGA   : player field goal attempts (until)
	-- - Pts   : player points (until)
	-- - FTM   : player free throws made (until)
	-- - qAst  : assist adjustment factor (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou.
	-- - qAst dolazi iz prethodne TEMP stavke.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 6: PtsGen_FG';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_ptsgen_fg;
	
	CREATE TEMP TABLE tmp_pl_ptsgen_fg AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    CASE
	        WHEN p.fga_until_day > 0
	        THEN
	            2
	            *
	            (
	                p.fgm_until_day
	                + 0.5 * p.fg3_made_until_day
	            )
	            *
	            (
	                1
	                -
	                0.5
	                *
	                (
	                    (p.points_until_day - p.ftm_until_day)::numeric
	                    / (2 * p.fga_until_day)
	                )
	                *
	                qa.q_ast_until
	            )
	        ELSE 0
	    END AS ptsgen_fg_until
	
	FROM mtr.player_per_params p
	JOIN tmp_pl_q_ast qa
	  ON qa.season_code = p.season_code
	 AND qa.game_code   = p.game_code
	 AND qa.team_code   = p.team_code
	 AND qa.player_code = p.player_code
	WHERE p.season_code = p_season_code;

	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
			------------------------------------------------------------------
	-- STEP 7: PtsGen_Ast (Points Generated from Assists)
	--
	-- Formula:
	-- PtsGen_Ast =
	-- 2 * [ (TeFGM - FGM + 0.5 * (Te3PM - 3PM)) / (TeFGM - FGM) ]   * 0.5 * [ ((TePts - TeFTM) - (Pts - FTM)) / (2 * (TeFGA - FGA)) ]* Ast
	--
	-- Gde je:
	-- - Ast   : player assists (until)
	-- - FGM   : player field goals made (until)
	-- - FGA   : player field goal attempts (until)
	-- - 3PM   : player 3pt field goals made (until)
	-- - Pts   : player points (until)
	-- - FTM   : player free throws made (until)
	--
	-- - TeFGM : team field goals made (until)
	-- - TeFGA : team field goal attempts (until)
	-- - Te3PM : team 3pt field goals made (until)
	-- - TePts : team points (until)
	-- - TeFTM : team free throws made (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou uz TEAM kontekst.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 7: PtsGen_Ast';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_ptsgen_ast;
	
	CREATE TEMP TABLE tmp_pl_ptsgen_ast AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    CASE
	        WHEN
	            (t.te_fg_made_until_day - p.fgm_until_day) > 0
	            AND (t.te_fg_att_until_day - p.fga_until_day) > 0
	        THEN
	            2
	            *
	            (
	                (
	                    (t.te_fg_made_until_day - p.fgm_until_day)
	                    + 0.5
	                      * (t.te_fg3_made_until_day - p.fg3_made_until_day)
	                )
	                / NULLIF(
	                    (t.te_fg_made_until_day - p.fgm_until_day),
	                    0
	                )
	            )
	            *
	            0.5
	            *
	            (
	                (
	                    (t.te_points_until_day - t.te_ft_made_until_day)
	                    - (p.points_until_day - p.ftm_until_day)
	                )
	                /
	                NULLIF(
	                    2 * (t.te_fg_att_until_day - p.fga_until_day),
	                    0
	                )
	            )
	            *
	            p.ast_until_day
	        ELSE 0
	    END AS ptsgen_ast_until
	
	FROM mtr.player_per_params p
	JOIN mtr.team_per_params t
	  ON t.season_code = p.season_code
	 AND t.game_code   = p.game_code
	 AND t.team_code   = p.team_code
	WHERE p.season_code = p_season_code;


	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);

	   ------------------------------------------------------------------
	-- STEP 8: PtsGen_OR (Points Generated from Offensive Rebounds)
	--
	-- Formula:
	-- PtsGen_OR =
	-- OR * TeORW * TePl%
	-- * [ TePts /
	--     ( TeFGM
	--       + [1 - (1 - TeFTM / TeFTA)^2] * 0.4 * TeFTA )
	--   ]
	--
	-- Gde je:
	-- - OR      : player offensive rebounds (until)
	-- - TeORW   : team offensive rebound weight (until)
	-- - TePl%   : team play percentage (until)
	-- - TePts   : team points (until)
	-- - TeFGM   : team field goals made (until)
	-- - TeFTM   : team free throws made (until)
	-- - TeFTA   : team free throws attempted (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Team scoring possessions u imenitelju su
	--   ekvivalentni TeScPoss.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 8: PtsGen_OR';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_ptsgen_or;
	
	CREATE TEMP TABLE tmp_pl_ptsgen_or AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    CASE
	        WHEN
	            p.offr_until_day > 0
	            AND sc.te_sc_poss_until > 0
	        THEN
	            p.offr_until_day
	            * orw.te_orw_until
	            * pl.te_pl_pct_until
	            *
	            (
	                t.te_points_until_day
	                /
	                NULLIF(sc.te_sc_poss_until, 0)
	            )
	        ELSE 0
	    END AS ptsgen_or_until
	
	FROM mtr.player_per_params p
	JOIN mtr.team_per_params t
	  ON t.season_code = p.season_code
	 AND t.game_code   = p.game_code
	 AND t.team_code   = p.team_code
	JOIN tmp_orw orw
	  ON orw.season_code = p.season_code
	 AND orw.game_code   = p.game_code
	 AND orw.team_code   = p.team_code
	JOIN tmp_pl_pct pl
	  ON pl.season_code = p.season_code
	 AND pl.game_code   = p.game_code
	 AND pl.team_code   = p.team_code
	JOIN tmp_sc_poss sc
	  ON sc.season_code = p.season_code
	 AND sc.game_code   = p.game_code
	 AND sc.team_code   = p.team_code
	WHERE p.season_code = p_season_code;

	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		 ------------------------------------------------------------------
	-- STEP 9: Total Points Generated (PtsGen)
	--
	-- Formula:
	-- PtsGen =
	-- (PtsGen_FG + PtsGen_Ast + FTM) * a
	-- + PtsGen_OR
	--
	-- Gde je:
	-- - PtsGen_FG  : points generated from field goals (until)
	-- - PtsGen_Ast : points generated from assists (until)
	-- - FTM        : player free throws made (until)
	-- - a          : team adjustment factor (until)
	-- - PtsGen_OR  : points generated from offensive rebounds (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until / *_until_day).
	-- - a je TEAM-level korektiv, primenjen na PLAYER output.
	-- - Ovo je poslednji "construction" korak pre OffRtg.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
    v_step_name := 'STEP 9: PtsGen';
    v_step_start := clock_timestamp();
	
	DROP TABLE IF EXISTS tmp_pl_ptsgen;
	
	CREATE TEMP TABLE tmp_pl_ptsgen AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    (
	        (
	            fg.ptsgen_fg_until
	            + ast.ptsgen_ast_until
	            + p.ftm_until_day
	        )
	        * a.te_a_until
	    )
	    +
	    orr.ptsgen_or_until
	    AS ptsgen_until
	
	FROM mtr.player_per_params p
	JOIN tmp_pl_ptsgen_fg fg
	  ON fg.season_code = p.season_code
	 AND fg.game_code   = p.game_code
	 AND fg.team_code   = p.team_code
	 AND fg.player_code = p.player_code
	JOIN tmp_pl_ptsgen_ast ast
	  ON ast.season_code = p.season_code
	 AND ast.game_code   = p.game_code
	 AND ast.team_code   = p.team_code
	 AND ast.player_code = p.player_code
	JOIN tmp_pl_ptsgen_or orr
	  ON orr.season_code = p.season_code
	 AND orr.game_code   = p.game_code
	 AND orr.team_code   = p.team_code
	 AND orr.player_code = p.player_code
	JOIN tmp_te_a a
	  ON a.season_code = p.season_code
	 AND a.game_code   = p.game_code
	 AND a.team_code   = p.team_code
	WHERE p.season_code = p_season_code;


	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
	    ------------------------------------------------------------------
	-- STEP 10: ScPoss_FG (Scoring Possessions from Field Goals)
	--
	-- Formula:
	-- ScPoss_FG =
	-- FGM * (1 - 0.5 * ((Pts - FTM) / (2 * FGA)) * qAst)
	--
	-- Gde je:
	-- - FGM   : player field goals made (until)
	-- - FGA   : player field goal attempts (until)
	-- - Pts   : player points (until)
	-- - FTM   : player free throws made (until)
	-- - qAst  : assist adjustment factor (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou.
	-- - qAst dolazi iz prethodne TEMP stavke.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 10: ScPoss_FG';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_scposs_fg;
	
	CREATE TEMP TABLE tmp_pl_scposs_fg AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    CASE
	        WHEN p.fga_until_day > 0
	        THEN
	            p.fgm_until_day
	            *
	            (
	                1
	                -
	                0.5
	                *
	                (
	                    (p.points_until_day - p.ftm_until_day)::numeric
	                    / (2 * p.fga_until_day)
	                )
	                *
	                qa.q_ast_until
	            )
	        ELSE 0
		    END AS scposs_fg_until
		
		FROM mtr.player_per_params p
		JOIN tmp_pl_q_ast qa
		  ON qa.season_code = p.season_code
		 AND qa.game_code   = p.game_code
		 AND qa.team_code   = p.team_code
		 AND qa.player_code = p.player_code
		WHERE p.season_code = p_season_code;

		RAISE NOTICE '% duration: % ms',
	    v_step_name,
	    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		    ------------------------------------------------------------------
	-- STEP 11: ScPoss_Ast (Scoring Possessions from Assists)
	--
	-- Formula:
	-- ScPoss_Ast =
	-- 0.5 * [ ((TePts - TeFTM) - (Pts - FTM)) / (2 * (TeFGA - FGA)) ] * Ast
	--
	-- Gde je:
	-- - Ast   : player assists (until)
	-- - Pts   : player points (until)
	-- - FTM   : player free throws made (until)
	-- - FGA   : player field goal attempts (until)
	--
	-- - TePts : team points (until)
	-- - TeFTM : team free throws made (until)
	-- - TeFGA : team field goal attempts (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou uz TEAM kontekst.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 11: ScPoss_Ast';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_scposs_ast;
	
	CREATE TEMP TABLE tmp_pl_scposs_ast AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    CASE
	        WHEN (t.te_fg_att_until_day - p.fga_until_day) > 0
	        THEN
	            0.5
	            *
	            (
	                (
	                    (t.te_points_until_day - t.te_ft_made_until_day)
	                    - (p.points_until_day - p.ftm_until_day)
	                )::numeric
	                /
	                NULLIF(
	                    2 * (t.te_fg_att_until_day - p.fga_until_day),
	                    0
	                )
	            )
	            *
	            p.ast_until_day
	        ELSE 0
	    END AS scposs_ast_until
	
	FROM mtr.player_per_params p
	JOIN mtr.team_per_params t
	  ON t.season_code = p.season_code
	 AND t.game_code   = p.game_code
	 AND t.team_code   = p.team_code
	WHERE p.season_code = p_season_code;

	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
    
		------------------------------------------------------------------
	-- STEP 12: ScPoss_FT (Scoring Possessions from Free Throws)
	--
	-- Formula:
	-- ScPoss_FT =
	-- [ 1 - (1 - FTM / FTA)^2 ] * 0.4 * FTA
	--
	-- Gde je:
	-- - FTM : player free throws made (until)
	-- - FTA : player free throws attempted (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 12:  ScPoss_FT';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_scposs_ft;
	
	CREATE TEMP TABLE tmp_pl_scposs_ft AS
	SELECT
	    season_code,
	    game_date,
	    game_code,
	    team_code,
	    player_code,
	
	    CASE
	        WHEN fta_until_day > 0
	        THEN
	            (
	                1
	                - POWER(
	                    1 - ftm_until_day::numeric / fta_until_day,
	                    2
	                )
	            )
	            * 0.4
	            * fta_until_day
	        ELSE 0
	    END AS scposs_ft_until
	
	FROM mtr.player_per_params
	WHERE season_code = p_season_code;
	
	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		------------------------------------------------------------------
	-- STEP 13: ScPoss_OR (Scoring Possessions from Offensive Rebounds)
	--
	-- Formula:
	-- ScPoss_OR = OR * TeORW * TePl%
	--
	-- Gde je:
	-- - OR     : player offensive rebounds (until)
	-- - TeORW  : team offensive rebound weight (until)
	-- - TePl%  : team play percentage (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou uz TEAM kontekst.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 13:  ScPoss_OR';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_scposs_or;
	
	CREATE TEMP TABLE tmp_pl_scposs_or AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    p.offr_until_day
	    * orw.te_orw_until
	    * pl.te_pl_pct_until
	    AS scposs_or_until
	
	FROM mtr.player_per_params p
	JOIN tmp_orw orw
	  ON orw.season_code = p.season_code
	 AND orw.game_code   = p.game_code
	 AND orw.team_code   = p.team_code
	JOIN tmp_pl_pct pl
	  ON pl.season_code = p.season_code
	 AND pl.game_code   = p.game_code
	 AND pl.team_code   = p.team_code
	WHERE p.season_code = p_season_code;

	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		------------------------------------------------------------------
	-- STEP 14: FGxPoss (Missed FG Possessions, OR-adjusted)
	--
	-- Formula:
	-- FGxPoss = (FGA - FGM) * (1 - 1.07 * TeOR%)
	--
	-- Gde je:
	-- - FGA    : player field goal attempts (until)
	-- - FGM    : player field goals made (until)
	-- - TeOR%  : team offensive rebound percentage (until)
	--            TeOR% = TeOR / (TeOR + TeDR)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - TeOR% je TEAM kontekst.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 14:  FGxPoss';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_fgxposs;
	
	CREATE TEMP TABLE tmp_pl_fgxposs AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    (p.fga_until_day - p.fgm_until_day)
	    *
	    (
	        1
	        - 1.07
	        *
	        CASE
	            WHEN (t.te_off_rebounds_until_day + t.te_def_rebounds_until_day) > 0
	            THEN
	                t.te_off_rebounds_until_day::numeric
	                /
	                (t.te_off_rebounds_until_day + t.te_def_rebounds_until_day)
	            ELSE 0
	        END
	    ) AS fgxposs_until
	
	FROM mtr.player_per_params p
	JOIN mtr.team_per_params t
	  ON t.season_code = p.season_code
	 AND t.game_code   = p.game_code
	 AND t.team_code   = p.team_code
	WHERE p.season_code = p_season_code;


	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
	    ------------------------------------------------------------------
	-- STEP 15: FTxPoss (Missed Free Throw Possessions)
	--
	-- Formula:
	-- FTxPoss = (1 - FTM / FTA)^2 * 0.4 * FTA
	--
	-- Gde je:
	-- - FTM : player free throws made (until)
	-- - FTA : player free throws attempted (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - Računa se na PLAYER nivou.
	-- - FTxPoss predstavlja posede izgubljene na liniji bacanja.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 15:  FTxPoss';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_ftxposs;
	
	CREATE TEMP TABLE tmp_pl_ftxposs AS
	SELECT
	    season_code,
	    game_date,
	    game_code,
	    team_code,
	    player_code,
	
	    CASE
	        WHEN fta_until_day > 0
	        THEN
	            POWER(
	                1 - ftm_until_day::numeric / fta_until_day,
	                2
	            )
	            * 0.4
	            * fta_until_day
	        ELSE 0
	    END AS ftxposs_until
	
	FROM mtr.player_per_params
	WHERE season_code = p_season_code;
	
	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
		------------------------------------------------------------------
	-- STEP 16: Total Possessions (PossTot)
	--
	-- Formula:
	-- PossTot =
	-- (ScPoss_FG + ScPoss_Ast + ScPoss_FT) * a
	-- + ScPoss_OR
	-- + FGxPoss
	-- + FTxPoss
	-- + TO
	--
	-- Gde je:
	-- - ScPoss_* : scoring possessions components (until)
	-- - a        : team adjustment factor (until)
	-- - FGxPoss  : missed FG possessions (until)
	-- - FTxPoss  : missed FT possessions (until)
	-- - TO       : player turnovers (until)
	--
	-- Napomena:
	-- - Svi ulazi su kumulativni (_until_day).
	-- - a je TEAM-level korekcija.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
	v_step_name := 'STEP 16: PossTot';
    v_step_start := clock_timestamp();
	DROP TABLE IF EXISTS tmp_pl_posstot;
	
	CREATE TEMP TABLE tmp_pl_posstot AS
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    (
	        (
	            fg.scposs_fg_until
	          + ast.scposs_ast_until
	          + ft.scposs_ft_until
	        )
	        * a.te_a_until
	    )
	    +
	    orp.scposs_or_until
	    +
	    fgx.fgxposs_until
	    +
	    ftx.ftxposs_until
	    +
	    p.tov_until_day
	    AS posstot_until
	
	FROM mtr.player_per_params p
	JOIN tmp_pl_scposs_fg fg
	  ON fg.season_code = p.season_code
	 AND fg.game_code   = p.game_code
	 AND fg.team_code   = p.team_code
	 AND fg.player_code = p.player_code
	JOIN tmp_pl_scposs_ast ast
	  ON ast.season_code = p.season_code
	 AND ast.game_code   = p.game_code
	 AND ast.team_code   = p.team_code
	 AND ast.player_code = p.player_code
	JOIN tmp_pl_scposs_ft ft
	  ON ft.season_code = p.season_code
	 AND ft.game_code   = p.game_code
	 AND ft.team_code   = p.team_code
	 AND ft.player_code = p.player_code
	JOIN tmp_pl_scposs_or orp
	  ON orp.season_code = p.season_code
	 AND orp.game_code   = p.game_code
	 AND orp.team_code   = p.team_code
	 AND orp.player_code = p.player_code
	JOIN tmp_pl_fgxposs fgx
	  ON fgx.season_code = p.season_code
	 AND fgx.game_code   = p.game_code
	 AND fgx.team_code   = p.team_code
	 AND fgx.player_code = p.player_code
	JOIN tmp_pl_ftxposs ftx
	  ON ftx.season_code = p.season_code
	 AND ftx.game_code   = p.game_code
	 AND ftx.team_code   = p.team_code
	 AND ftx.player_code = p.player_code
	JOIN tmp_te_a a
	  ON a.season_code = p.season_code
	 AND a.game_code   = p.game_code
	 AND a.team_code   = p.team_code
	WHERE p.season_code = p_season_code;
	
	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);
    ------------------------------------------------------------------
    -- x. FINAL OUTPUT: Player Offensive Rating
    ------------------------------------------------------------------

     ------------------------------------------------------------------
	-- STEP 17: Player Offensive Rating (FINAL OUTPUT)
	--
	-- Formula:
	-- OffRtg = (PtsGen / PossTot) * 100
	--
	-- Gde je:
	-- - PtsGen  : total points generated (until)
	-- - PossTot : total possessions (until)
	--
	-- Napomena:
	-- - Ovo je JEDINI trajni output ofanzivnog pipeline-a.
	-- - Sve prethodne metrike su TEMP i služe samo za konstrukciju.
	-- - Ograničeno na prosleđenu sezonu (p_season_code).
	------------------------------------------------------------------
    v_step_name := 'FINAL OUTPUT: Player Offensive Rating';
    v_step_start := clock_timestamp();
	TRUNCATE TABLE mtr.pl_off_offrtg;
	
	INSERT INTO mtr.pl_off_offrtg (
	    season_code,
	    game_date,
	    game_code,
	    team_code,
	    player_code,
	    offrtg_until
	)
	SELECT
	    p.season_code,
	    p.game_date,
	    p.game_code,
	    p.team_code,
	    p.player_code,
	
	    COALESCE(
        CASE
            WHEN poss.posstot_until > 0
            THEN
                100
                * pts.ptsgen_until
                / poss.posstot_until
            ELSE NULL
        END,
        0
    ) AS offrtg_until
	FROM mtr.player_per_params p
	JOIN tmp_pl_ptsgen pts
	  ON pts.season_code = p.season_code
	 AND pts.game_code   = p.game_code
	 AND pts.team_code   = p.team_code
	 AND pts.player_code = p.player_code
	JOIN tmp_pl_posstot poss
	  ON poss.season_code = p.season_code
	 AND poss.game_code   = p.game_code
	 AND poss.team_code   = p.team_code
	 AND poss.player_code = p.player_code
	WHERE p.season_code = p_season_code;

	RAISE NOTICE '% duration: % ms',
    v_step_name,
    ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - v_step_start)) * 1000);

END;
$BODY$;

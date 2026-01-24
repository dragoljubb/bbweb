-- MTR pipeline order

INSERT INTO ctl.pipeline_steps (layer, step_order, procedure_name, description)
VALUES
('mtr', 10, 'mtr.rebuild_lg_per_params', 'League PER params – matchday snapshot');

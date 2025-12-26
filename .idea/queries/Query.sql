
select code, phasetype_name, alias_name, default_order
from dwh.phase_types
WHERE code = 'RS'
limit 10

select *
from dwh.seasons
WHERE comp_code = 'E'

Alter TABLE
    select * from rounds_old;
select *
from dwh.rounds_old
limit ;
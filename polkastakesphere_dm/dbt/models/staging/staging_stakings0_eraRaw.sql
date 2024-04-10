/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

select
    era,
    ts,
    sum(validator_staking_rewards) / count(*) as avg_validator_staking_rewards,
    sum(validator_staking_rewards) as total_era_rewards,
    count(*) as active_validator_cnt
from
    {{ source('main', 'raw_stakings') }}
where
    storage = 'ErasStakers'
    and validator_total is not null
group by
    era,
    ts

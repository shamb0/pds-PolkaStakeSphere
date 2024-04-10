/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

select
    v.*,
    e.avg_validator_staking_rewards,
    case
        when v.validator_staking_rewards is null then null
        else
            365 * (1 - v.validator_commission) * e.avg_validator_staking_rewards / v.validator_total
    end as validator_normalized_staking_apr
from
    {{ ref('staging_stakings0_validators') }} as v
left join
    {{ ref('staging_stakings0_eraRaw') }} as e
    on
        v.era = e.era
        and v.ts = e.ts

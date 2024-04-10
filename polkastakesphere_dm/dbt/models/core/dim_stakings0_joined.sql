/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

select
    a.validator,
    a.era,
    a.ts,
    a.date,
    va.validator_is_active,
    va.validator_total,
    va.validator_own,
    va.validator_commission,
    va.validator_reward_shares,
    va.validator_reward_points,
    va.validator_staking_rewards,
    va.validator_staking_apr,
    va.validator_effective_staking_apr,
    va.validator_normalized_staking_apr,
    a.nominatorcnt,
    a.nominators
from
    {{ ref('staging_stakings0_aggregated') }} as a
left join
    {{ ref('staging_stakings0_validator_augmented') }} as va
    on
        a.validator = va.validator
        and a.era = va.era
        and a.ts = va.ts

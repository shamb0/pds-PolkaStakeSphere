/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

select
    v.era,
    v.ts,
    address_ss58 as validator,
    not coalesce(validator_total is null, false) as validator_is_active,
    validator_total,
    validator_own,
    validator_commission,
    validator_reward_shares,
    validator_reward_points,
    validator_staking_rewards,
    case
        when validator_staking_rewards is null then null
        else 365 * validator_staking_rewards / validator_total
    end as validator_staking_apr,
    case
        when validator_staking_rewards is null then null
        else 365 * (1 - validator_commission) * validator_staking_rewards / validator_total
    end as validator_effective_staking_apr
from
    {{ source('main', 'raw_stakings') }} as v
where
    storage = 'ErasStakers'

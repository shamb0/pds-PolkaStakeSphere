/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

with recursive flattened_targets (nominator, era, ts, date, pv, index, target) as (
    select
        address_ss58 as nominator,
        era,
        ts,
        date,
        pv,
        0 as index,
        json_extract_string(pv, '$.targets[0]') as target
    from {{ source('main', 'raw_stakings') }}
    where storage = 'Nominators'
    union all
    select
        f.nominator,
        f.era,
        f.ts,
        f.date,
        f.pv,
        f.index + 1 as index,
        json_extract_string(f.pv, '$.targets[' || f.index + 1 || ']') as target
    from flattened_targets as f
    where json_extract_string(f.pv, '$.targets[' || f.index + 1 || ']') is not null
),

final_targets as (
    select
        nominator,
        era,
        ts,
        date,
        regexp_replace(target, '"', '', 'g') as target
    from flattened_targets
)

select * from final_targets

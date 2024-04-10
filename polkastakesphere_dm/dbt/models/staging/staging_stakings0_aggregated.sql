/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

select
    target as validator,
    era,
    ts,
    date,
    listagg(nominator) as nominators,
    count(*) as nominatorcnt
from {{ ref('staging_stakings0_unnested') }}
group by target, era, date, ts

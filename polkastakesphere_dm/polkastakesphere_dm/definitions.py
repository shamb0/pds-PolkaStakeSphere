
from dagster import Definitions
from dagster import file_relative_path
from dagster import load_assets_from_modules
from dagster_dbt import DbtCliResource
from dagster_dbt import load_assets_from_dbt_project

from .assets import stakings
from .resources import SubstrateStakingResource

DBT_PROJECT_PATH = file_relative_path(__file__, "../dbt")
POLKASTAKESPHERE_CONFIG_PATH = file_relative_path(__file__, "../../config/PolkaStakeSphere_dev_config.yaml")

# Resource Initialization
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_PATH, profiles_dir=DBT_PROJECT_PATH)
polka_stake_sphere_config = SubstrateStakingResource.load_config(config_file_path=POLKASTAKESPHERE_CONFIG_PATH)

model_resources = {
    "dbt": dbt_resource,
    "substrate_etl_cfg": SubstrateStakingResource(
            gcp_project_id=polka_stake_sphere_config.gcp_project_id,
            gcp_substrate_ds_id=polka_stake_sphere_config.gcp_substrate_ds_id,
            gcp_polkadot_staking_table_id=polka_stake_sphere_config.staking0["gcp_polkadot_staking_table_id"],
            gcp_materialize_table_id=polka_stake_sphere_config.gcp_materialize_table_id,
            gcp_polkadot_staking_column_ts=polka_stake_sphere_config.staking0["gcp_polkadot_staking_column_ts"]
        )
}

dbt_assets = load_assets_from_dbt_project(DBT_PROJECT_PATH, DBT_PROJECT_PATH)
all_assets = load_assets_from_modules([stakings])

defs = Definitions(assets=[*dbt_assets, *all_assets], resources=model_resources)

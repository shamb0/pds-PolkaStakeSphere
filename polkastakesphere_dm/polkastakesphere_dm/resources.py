from dagster import ConfigurableResource
from pydantic import BaseModel
from pydantic import ValidationError
from ruamel import yaml


class PolkaStakeSphereConfig(BaseModel):
    gcp_project_id: str
    gcp_substrate_ds_id: str
    gcp_materialize_table_id: str
    staking0: dict

# Resource class
class SubstrateStakingResource(ConfigurableResource):
    gcp_project_id: str
    gcp_substrate_ds_id: str
    gcp_polkadot_staking_table_id: str
    gcp_materialize_table_id: str
    gcp_polkadot_staking_column_ts: str

    @staticmethod
    def load_config(config_file_path: str) -> PolkaStakeSphereConfig:
        try:
            with open(config_file_path) as f:
                yaml_inst = yaml.YAML(typ="safe", pure=True)
                config_data = yaml_inst.load(f)
            return PolkaStakeSphereConfig(**config_data["PolkaStakeSphere"])
        except (FileNotFoundError, ValidationError) as e:
                raise ValueError(f"Configuration file {f} load error: {e}")

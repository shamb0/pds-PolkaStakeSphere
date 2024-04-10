from dagster import AssetExecutionContext
from dagster import asset

from ..resources import SubstrateStakingResource
from .asset_exec_params import SubstrateExtractParameters
from .batch_proc import build_substrate_query
from .batch_proc import process_data


@asset(compute_kind="python")
def raw_stakings(context: AssetExecutionContext, substrate_etl_cfg: SubstrateStakingResource) -> None:
    params = SubstrateExtractParameters(
        start_date="2024-04-01",
        end_date="2024-04-03",
        gcp_project=substrate_etl_cfg.gcp_project_id,
        gcp_dataset=substrate_etl_cfg.gcp_substrate_ds_id,
        gcp_table=substrate_etl_cfg.gcp_polkadot_staking_table_id,
        timestamp_column=substrate_etl_cfg.gcp_polkadot_staking_column_ts,
        gcp_materialize_dataset=substrate_etl_cfg.gcp_materialize_table_id,
        sink_update_mode="overwrite",
        destination="local",
    )

    try:
        # Extract data from BigQuery
        context.log.info("Starting data extraction from BigQuery")
        process_data(context, params, query_str=build_substrate_query(context, params))
        context.log.info("Data extraction completed successfully")
    except Exception as e:
        context.log.error(f"Error occurred during main: {e!s}")
        raise e

    # Log some metadata about the table we just wrote. It will show up in the UI.
    context.add_output_metadata({"num_rows": "TODO 0x00"})

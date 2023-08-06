from alvin_integration.interfaces.config import AbstractProducerConfig
from alvin_integration.models import AlvinPatch
from alvin_integration.producers.dbt.patch.functions import after_run, execute, before_run
from alvin_integration.producers.dbt.patch.functions_144 import execute as execute_144
from alvin_integration.producers.dbt.patch.functions_legacy import execute as execute_legacy
from alvin_integration.producers.dbt.patch.functions_legacy import before_run as before_run_legacy


class DBTProducerConfig(AbstractProducerConfig):
    @property
    def producer_name(self):
        return "dbt"

    def get_patching_list(self):
        return [
            AlvinPatch(
                package_name="dbt-core",
                function=before_run_legacy,
                supported_versions=["1.0.0", "1.0.1"],
                destination_path="dbt.task.run.RunTask",
            ),
            AlvinPatch(
                package_name="dbt-core",
                function=before_run,
                supported_versions=["1.2.0", "1.2.1", "1.2.2", "1.4.0", "1.4.1", "1.4.2", "1.4.3", "1.4.4", "1.4.5",
                                    "1.4.6"],
                destination_path="dbt.task.run.RunTask",
            ),
            AlvinPatch(
                package_name="dbt-core",
                function=after_run,
                supported_versions=["1.0.0", "1.0.1", "1.2.0", "1.2.1", "1.2.2", "1.4.0", "1.4.1", "1.4.2", "1.4.3",
                                    "1.4.4", "1.4.5", "1.4.6"],
                destination_path="dbt.task.run.RunTask",
            ),
            AlvinPatch(
                package_name="dbt-core",
                function=execute,
                supported_versions=["1.2.0", "1.2.1", "1.2.2"],
                destination_path="dbt.adapters.bigquery.connections.BigQueryConnectionManager",
            ),
            AlvinPatch(
                package_name="dbt-core",
                function=execute_144,
                supported_versions=["1.4.0", "1.4.1", "1.4.2", "1.4.3", "1.4.4", "1.4.5", "1.4.6"],
                destination_path="dbt.adapters.bigquery.connections.BigQueryConnectionManager",
            ),
            AlvinPatch(
                package_name="dbt-core",
                function=execute_legacy,
                supported_versions=["1.0.0", "1.0.1"],
                destination_path="dbt.adapters.bigquery.connections.BigQueryConnectionManager",
            ),
        ]

    def get_lineage_config(self):
        pass

    def get_target_packages(self):
        return ["dbt-core"]

    def get_target_pipelines(self):
        pass

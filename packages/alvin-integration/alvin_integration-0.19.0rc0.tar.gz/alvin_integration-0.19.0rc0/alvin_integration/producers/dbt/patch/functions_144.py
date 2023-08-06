# overrides https://github.com/dbt-labs/dbt-bigquery/blob/main/dbt/adapters/bigquery/connections.py#L442
def execute(self, sql, auto_begin=False, fetch=None):
    from alvin_integration.producers.dbt.lineage.extractors.bigquery import (
        AlvinBigQueryAdapterResponse,
    )
    from dbt.clients import agate_helper

    from datetime import datetime, timezone
    event_time = datetime.now(timezone.utc)

    sql = self._add_query_comment(sql)
    # auto_begin is ignored on bigquery, and only included for consistency
    query_job, iterator = self.raw_execute(sql, fetch=fetch)

    if fetch:
        table = self.get_table_from_response(iterator)
    else:
        table = agate_helper.empty_table()

    message = "OK"
    code = None
    num_rows = None
    bytes_processed = None
    location = None
    job_id = None
    project_id = None
    num_rows_formatted = None
    processed_bytes = None
    slot_ms = None

    if query_job.statement_type == "CREATE_VIEW":
        code = "CREATE VIEW"

    elif query_job.statement_type == "CREATE_TABLE_AS_SELECT":
        code = "CREATE TABLE"
        conn = self.get_thread_connection()
        client = conn.handle
        query_table = client.get_table(query_job.destination)
        num_rows = query_table.num_rows

    elif query_job.statement_type == "SCRIPT":
        code = "SCRIPT"

    elif query_job.statement_type in ["INSERT", "DELETE", "MERGE", "UPDATE"]:
        code = query_job.statement_type
        num_rows = query_job.num_dml_affected_rows

    elif query_job.statement_type == "SELECT":
        code = "SELECT"
        conn = self.get_thread_connection()
        client = conn.handle
        # use anonymous table for num_rows
        query_table = client.get_table(query_job.destination)
        num_rows = query_table.num_rows

    # set common attributes
    bytes_processed = query_job.total_bytes_processed
    slot_ms = query_job.slot_millis
    processed_bytes = self.format_bytes(bytes_processed)
    location = query_job.location
    job_id = query_job.job_id
    project_id = query_job.project
    if num_rows is not None:
        num_rows_formatted = self.format_rows_number(num_rows)
        message = f"{code} ({num_rows_formatted} rows, {processed_bytes} processed)"
    elif bytes_processed is not None:
        message = f"{code} ({processed_bytes} processed)"
    else:
        message = f"{code}"

    if location is not None and job_id is not None and project_id is not None:
        from dbt.events import AdapterLogger
        logger = AdapterLogger("BigQuery")
        logger.debug(self._bq_job_link(location, project_id, job_id))

    response = AlvinBigQueryAdapterResponse(
        event_time=event_time,
        _message=message,
        rows_affected=num_rows,
        code=code,
        bytes_processed=bytes_processed,
        started=query_job.started,
        ended=query_job.ended,
        location=location,
        project_id=project_id,
        job_id=job_id,
        slot_ms=slot_ms,
    )

    return response, table

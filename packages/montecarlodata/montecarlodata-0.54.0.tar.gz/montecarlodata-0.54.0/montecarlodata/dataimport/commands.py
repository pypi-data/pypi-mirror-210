import click
from typing import Dict, Optional
from uuid import UUID

from pycarlo.features.dbt import DbtImporter

from montecarlodata.common.common import create_mc_client
from montecarlodata.dataimport.dbt import DbtImportService


@click.group(help="Import data.", name="import")
def import_subcommand():
    """
    Group for any import related subcommands
    """
    pass


@import_subcommand.command()
@click.option(
    "--project-name",
    type=click.STRING,
    default="default-project",
    show_default=True,
    help="Project name (perhaps a logical group of dbt models, analogous to a project in dbt Cloud)",
)
@click.option(
    "--job-name",
    type=click.STRING,
    default="default-job",
    show_default=True,
    help="Job name (perhaps a logical sequence of dbt executions, analogous to a job in dbt Cloud)",
)
@click.option(
    "--manifest",
    type=click.Path(exists=True),
    required=True,
    help="Path to the dbt manifest file (manifest.json)",
)
@click.option(
    "--run-results",
    type=click.Path(exists=True),
    required=True,
    help="Path to the dbt run results file (run_results.json)",
)
@click.option(
    "--logs",
    type=click.Path(exists=True),
    required=False,
    help="Path to a file containing dbt run logs",
)
@click.option(
    "--connection-id",
    type=click.UUID,
    required=False,
    help="Identifier of warehouse or lake connection to use to resolve dbt models to tables. "
    "Required if you have more than one warehouse or lake connection.",
)
@click.pass_obj
def dbt_run(
    ctx: Dict,
    project_name: str,
    job_name: str,
    manifest: str,
    run_results: str,
    logs: Optional[str],
    connection_id: Optional[UUID],
):
    """
    Import dbt run artifacts.
    """
    DbtImportService(config=ctx["config"], mc_client=create_mc_client(ctx)).import_run(
        project_name=project_name,
        job_name=job_name,
        manifest_path=manifest,
        run_results_path=run_results,
        logs_path=logs,
        connection_id=connection_id,
    )


@import_subcommand.command()
@click.argument("MANIFEST_FILE", required=True, type=click.Path(exists=True))
@click.option(
    "--project-name",
    required=False,
    type=click.STRING,
    help="Name that uniquely identifies dbt project.",
)
@click.option(
    "--batch-size",
    required=False,
    default=10,
    type=click.INT,
    help="Number of DBT manifest nodes to send in each batch."
    "Use smaller number if requests are timing out."
    "Use larger number for higher throughput.",
)
@click.option(
    "--default-resource",
    required=False,
    type=click.STRING,
    help="The warehouse friendly name or UUID where dbt objects will be associated with.",
)
@click.option(
    "--async/--no-async",
    "do_async",
    default=True,
    show_default=True,
    help="Toggle asynchronous processing of dbt manifest file",
)
@click.pass_obj
def dbt_manifest(
    ctx, manifest_file, project_name, batch_size, default_resource, do_async
):
    """
    Import dbt manifest (DEPRECATED).

    This command has been deprecated and will be removed in a future release. Please use `import dbt-run` instead.
    """
    importer = DbtImporter(mc_client=create_mc_client(ctx), print_func=click.echo)
    import_func = (
        importer.upload_dbt_manifest if do_async else importer.import_dbt_manifest
    )
    import_func(
        dbt_manifest=manifest_file,
        project_name=project_name,
        batch_size=batch_size,
        default_resource=default_resource,
    )


@import_subcommand.command()
@click.argument("RUN_RESULTS_FILE", required=True, type=click.Path(exists=True))
@click.option(
    "--project-name",
    required=False,
    type=click.STRING,
    help="Name that uniquely identifies dbt project.",
)
@click.option(
    "--async/--no-async",
    "do_async",
    default=True,
    show_default=True,
    help="Toggle asynchronous processing of dbt run results file",
)
@click.pass_obj
def dbt_run_results(ctx, run_results_file, project_name, do_async):
    """
    Import dbt run results (DEPRECATED).

    This command has been deprecated and will be removed in a future release. Please use `import dbt-run` instead.
    """
    importer = DbtImporter(mc_client=create_mc_client(ctx), print_func=click.echo)
    import_func = (
        importer.upload_run_results if do_async else importer.import_run_results
    )
    import_func(dbt_run_results=run_results_file, project_name=project_name)

import os
import pathlib
import requests
from invoke import Runner, Collection, Result, task

from .selflib import getInventory, os_exe_async


INVENTORY = getInventory(os.getenv("INVENTORY_FILE"))
PATH_TO_SCRIPTS = pathlib.Path(__file__).parent / "groovy"


def get_base_command_cli(server):
    return INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])


@task
def export_all_jobs(ctx: Runner, server: str):
    """Экспортировать указанную Job из Jenkins"""
    base_command_cli = get_base_command_cli(server)
    pathlib.Path("data", server, "jobs").mkdir(parents=True, exist_ok=True)
    # Получить список всех Job
    jobs: Result = ctx.run(f"{base_command_cli} list-jobs", hide=True).stdout.split(
        "\n"
    )
    # Перебрать в цикле все job и скачать их в XML
    commands = [(f'{base_command_cli} get-job "{job}"', job) for job in jobs if job]
    print("count jobs: ", len(commands))
    # Выполнить команды асинхронно
    os_exe_async(
        commands,
        handle=lambda label, stdout, stderr, cod, cmd: pathlib.Path(
            "data", server, "jobs", f"{label}.xml"
        ).write_text(stdout),
    )


@task
def export_job(ctx: Runner, server: str, jobname: str):
    """Экспортировать все Job из Jenkins"""
    pathlib.Path("data", server, "jobs").mkdir(parents=True, exist_ok=True)
    res: Result = ctx.run(
        f"{get_base_command_cli(server)} get-job {jobname}", hide=True
    )
    if not res.stderr:
        pathlib.Path("data", server, "jobs", f"{jobname}.xml").write_text(res.stdout)


@task
def create_job(ctx: Runner, server: str, jobname: str, from_server: str):
    """Создать указанную Job на Jenkins"""
    ctx.run(
        f"{get_base_command_cli(server)} create-job {jobname} < {pathlib.Path('data', from_server,'jobs',f'{jobname}.xml')}",
    )


@task
def update_job(ctx: Runner, server: str, jobname: str, from_server: str):
    """Обновить указанную Job в Jenkins"""
    ctx.run(
        f"{get_base_command_cli(server)} update-job {jobname} < {pathlib.Path('data',from_server,'jobs',f'{jobname}.xml')}",
    )


@task
def export_all_plugins(ctx: Runner, server: str):
    """Получить список всех плагинов"""

    path_to_script = (PATH_TO_SCRIPTS / "export_plugins.txt").resolve()

    res: Result = ctx.run(
        f"{get_base_command_cli(server)} groovy = < {path_to_script}", hide=False
    )

    if not res.stderr:
        pathlib.Path("data", server, "plugins.txt").write_text(res.stdout)


@task
def install_plugin(ctx: Runner, server: str, plugin: str):
    """Установить указанный плагин"""
    ctx.run(
        f"{get_base_command_cli(server)} install-plugin {plugin}",
    )
    print(f":> {plugin}")


@task
def install_all_plugin(ctx: Runner, server: str, from_file: str):
    """Установить все плагины"""
    for plugin in pathlib.Path(from_file).read_text().split("\n"):
        if plugin:
            install_plugin(ctx, server, plugin)


@task
def export_JCasC(ctx: Runner, server: str):
    """Загрузить настройки из плагина 'Jenkins Configuration as Code'"""
    i = INVENTORY[server]
    res: requests.Response = requests.post(
        f"http://{i['JENKINS_USER_ID']}:{i['JENKINS_API_TOKEN']}@{i['JENKINS_URL']}/configuration-as-code/export"
    )
    if res.status_code == 200 and res.text:
        pathlib.Path("data", server, "jenkins.yaml").write_text(res.text)


job_nsp = Collection()
job_nsp.add_task(export_all_jobs, "export-all")
job_nsp.add_task(export_job, "export")
job_nsp.add_task(create_job, "create")
job_nsp.add_task(update_job, "update")

plugins_nsp = Collection()
plugins_nsp.add_task(export_all_plugins, "export-all")
plugins_nsp.add_task(install_plugin, "install")
plugins_nsp.add_task(install_all_plugin, "all-install")

jcasc_nsp = Collection()
jcasc_nsp.add_task(export_JCasC, "export")

namespace = Collection()
namespace.add_collection(job_nsp, "job")
namespace.add_collection(plugins_nsp, "plugins")
namespace.add_collection(jcasc_nsp, "jcasc")

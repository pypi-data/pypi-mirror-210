import os
import pathlib

from invoke import Collection, Result, task

from .selflib import getInventory, os_exe_async


INVENTORY = getInventory(os.getenv("INVENTORY_FILE"))


@task
def export_all_jobs(ctx, server: str):
    """Экспортировать все Job с Jenkins"""
    base_command_cli = INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])
    pathlib.Path("data", server, "jobs").mkdir(parents=True, exist_ok=True)
    # Получить список всех Job
    jobs: Result = ctx.run(
        f"{base_command_cli} list-jobs",
    ).stdout.split("\n")
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
def create_job(ctx, server: str, jobname: str, in_folder):
    """Создать указанную Job на Jenkins"""
    base_command_cli = INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])

    res: Result = ctx.run(
        f"{base_command_cli} create-job {jobname} < {pathlib.Path('data', in_folder,'jobs',f'{jobname}.xml')}",
    )
    print(res)


@task
def update_job(ctx, server: str, jobname: str, in_folder):
    """Обновить указанный Job в Jenkins"""
    base_command_cli = INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])

    res: Result = ctx.run(
        f"{base_command_cli} update-job {jobname} < {pathlib.Path('data',in_folder,'jobs',f'{jobname}.xml')}",
    )
    print(res)


@task
def export_all_plugins(ctx, server: str):
    """Получить список всех плагинов"""
    base_command_cli = INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])

    res: Result = ctx.run(
        f"{base_command_cli} list-plugins",
    )
    print(res)
    if not res.stderr:
        pathlib.Path("data", server, "plains.txt").write_text(res.stdout)


@task
def install_plugins(ctx, server: str, plugin: str):
    """Установить указанный плагин"""
    base_command_cli = INVENTORY[server]["BASE_COMMAND_CLI"].format(**INVENTORY[server])

    res: Result = ctx.run(
        f"{base_command_cli} install-plugin {plugin}",
    )
    print(res)


@task
def my_task(ctx):
    print("!!")
    ctx.run("ls")


job_nsp = Collection()
job_nsp.add_task(export_all_jobs, "export-all")
job_nsp.add_task(create_job, "create")
job_nsp.add_task(update_job, "update")

plugins_nsp = Collection()
plugins_nsp.add_task(export_all_plugins, "export-all")
plugins_nsp.add_task(install_plugins, "install")
namespace = Collection()
namespace.add_collection(job_nsp, "job")
namespace.add_collection(plugins_nsp, "plugins")
namespace.add_task(my_task)

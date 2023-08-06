import typing
from asyncio import create_subprocess_shell, gather, run, subprocess
from typing import Callable, List, Tuple

import yaml


class type_os_res(typing.NamedTuple):
    stdout: str
    stderr: str
    cod: str
    cmd: str


def getInventory(path_to_inventory: str = None):
    if not path_to_inventory:
        path_to_inventory = "inventory.yml"
    with open(path_to_inventory, "r") as file:
        inventory = yaml.safe_load(file)
    return inventory


def divide_array(array: List, num_elements: int) -> List[Tuple[str, str]]:
    """Поделить переданный массив на указанное количество частей"""
    result = []
    for i in range(0, len(array), num_elements):
        result.append(array[i : i + num_elements])
    return result


def os_exe_async(
    commands: List[Tuple[str, str]],
    handle: Callable = type_os_res,
    divide_list: int = 10,
) -> List[type_os_res]:
    """
    Выполнить асинхронно команды OS, каждая команда в отдельной потоке
    """

    async def __self(
        _command: str,
        _label: str,
        _handle: Callable,
    ):
        # Выполняем команду
        proc = await create_subprocess_shell(
            cmd=_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        print(":>", _label)
        return _handle(
            label=_label,
            stdout=stdout.decode(),
            stderr=stderr.decode(),
            cod=proc.returncode,
            cmd=_command,
        )

    async def __loop(_cmds: List[Tuple[str, str]]):
        _task = (__self(_cmd, _label, handle) for _cmd, _label in _cmds)
        return await gather(*_task)

    da = divide_array(commands, divide_list)
    da_len = len(da)
    for index, cmd in enumerate(da):
        print(f"{index+1}/{da_len}")
        run(__loop(cmd))

import os.path
import re
import shutil
import subprocess
from ctypes_window_info import get_window_infos

startupinfo = subprocess.STARTUPINFO()
creationflags = 0 | subprocess.CREATE_NO_WINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
}
f = os.path.normpath(shutil.which("taskkill.exe"))


def _taskkill(cmd: str) -> tuple:
    """
    Executes the taskkill command with the provided command string.

    Args:
        cmd (str): The taskkill command to execute.

    Returns:
        tuple: A tuple containing the return code, stdout, and stderr of the command.
    """
    p = subprocess.run(
        cmd,
        capture_output=True,
        start_new_session=True,
        **invisibledict,
        shell=False,
    )
    return (
        p.returncode,
        p.stdout.decode("utf-8", "ignore"),
        p.stderr.decode("utf-8", "ignore"),
    )


def _get_iter(pids):
    """
    Converts a single PID or an iterable of PIDs to a list.

    Args:
        pids: A single PID or an iterable of PIDs.

    Returns:
        list: A list of PIDs.
    """
    if isinstance(pids, (str, int)):
        pids = [pids]
    return pids


def taskkill_pid(pids: str | list | tuple) -> list[tuple[int, str, str]]:
    """
    Kills the processes with the specified PIDs.

    Args:
        pids (str | list | tuple): The PIDs of the processes to kill.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing the return code, stdout, and stderr for each process killed.
    """
    results = []
    pids = _get_iter(pids)
    for pid in pids:
        results.append(_taskkill(f"{f} /PID {pid}"))
    return results


def taskkill_pid_children(pids: str | list | tuple) -> list[tuple[int, str, str]]:
    """
    Kills the processes with the specified PIDs along with their child processes.

    Args:
        pids (str | list | tuple): The PIDs of the processes to kill.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing the return code, stdout, and stderr for each process killed.
    """
    results = []
    pids = _get_iter(pids)
    for pid in pids:
        results.append(_taskkill(f"{f} /T /PID {pid}"))
    return results


def taskkill_force_pid(pids: str | list | tuple) -> list[tuple[int, str, str]]:
    """
    Forces the termination of processes with the specified PIDs.

    Args:
        pids (str | list | tuple): The PIDs of the processes to force kill.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing the return code, stdout, and stderr for each process terminated.
    """
    results = []
    pids = _get_iter(pids)
    for pid in pids:
        results.append(_taskkill(f"{f} /F /PID {pid}"))
    return results


def taskkill_force_pid_children(pids: str | list | tuple) -> list[tuple[int, str, str]]:
    """
    Forces the termination of processes with the specified PIDs along with their child processes.

    Args:
        pids (str | list | tuple): The PIDs of the processes to force kill.

    Returns:
        list[tuple[int, str, str]]: A list of tuples containing the return code, stdout, and stderr for each process terminated.
    """
    results = []

    pids = _get_iter(pids)
    for pid in pids:
        results.append(_taskkill(f"{f} /F /T /PID {pid}"))

    return results


def taskkill_regex_rearch(
    dryrun: bool = True,
    kill_children: bool = True,
    force_kill: bool = True,
    title: str = ".*",
    flags_title: int = re.I,
    windowtext: str = ".*",
    flags_windowtext: int = re.I,
    class_name: str = ".*",
    flags_class_name: int = re.I,
    path: str = ".*",
    flags_path: int = re.I,
) -> list:
    """
    Searches for and terminates processes matching the specified criteria.

    Args:
        dryrun (bool, optional): If True, only prints the windows that would be killed without actually terminating them. Defaults to True.
        kill_children (bool, optional): If True, terminates child processes along with the main processes. Defaults to True.
        force_kill (bool, optional): If True, forces the termination of processes. Defaults to True.
        title (str, optional): Regex pattern for the window title. Defaults to ".*".
        flags_title (int, optional): Flags for the window title regex pattern. Defaults to re.I.
        windowtext (str, optional): Regex pattern for the window text. Defaults to ".*".
        flags_windowtext (int, optional): Flags for the window text regex pattern. Defaults to re.I.
        class_name (str, optional): Regex pattern for the window class name. Defaults to ".*".
        flags_class_name (int, optional): Flags for the window class name regex pattern. Defaults to re.I.
        path (str, optional): Regex pattern for the process path. Defaults to ".*".
        flags_path (int, optional): Flags for the process path regex pattern. Defaults to re.I.

    Returns:
        list: A list of PIDs of the terminated processes if dryrun is False. Otherwise, prints the windows that would be killed.
    """
    titlere = re.compile(title, flags=flags_title)
    windowtextre = re.compile(windowtext, flags=flags_windowtext)
    class_namere = re.compile(class_name, flags=flags_class_name)
    pathre = re.compile(path, flags=flags_path)
    allwindows = get_window_infos()
    goodwindows = [
        x
        for x in allwindows
        if titlere.search(x.title)
        and windowtextre.search(x.windowtext)
        and class_namere.search(x.class_name)
        and pathre.search(x.path)
    ]
    pids = list(set([x.pid for x in goodwindows]))
    if not dryrun:
        if not kill_children and not force_kill:
            return taskkill_pid(pids)
        if kill_children and not force_kill:
            return taskkill_pid_children(pids)
        if not kill_children and force_kill:
            return taskkill_force_pid(pids)
        if kill_children and force_kill:
            return taskkill_force_pid_children(pids)
    else:
        print("Dry Run - would kill these windows:")
        for window in goodwindows:
            print(window)
    return pids





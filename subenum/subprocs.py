import asyncio
import sys
from termcolor import cprint


async def run_cmd(cmd, inp_src=None):
    cprint(f"[*] Started running: {cmd}", color="cyan", file=sys.stderr)
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate(input=inp_src)
    if stderr and not stdout:
        cprint(f"Failed running: {cmd}\n{stderr.decode()}",
               color="red", file=sys.stderr)
        return ""
    else:
        cprint(f"[*] Completed running: {cmd}",
               color="blue", file=sys.stderr)
        return stdout.decode()


async def run_cmds(*cmds):
    tasks = []
    for cmd in cmds:
        tasks.append(run_cmd(cmd))
    return await asyncio.gather(*tasks)

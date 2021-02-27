import asyncio


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def multiproc():
    await asyncio.gather(
        run('sleep 1; ls .'),
        run('ls /tmp'),
        run('sleep 1; echo "hello"')
    )


def main():
    asyncio.run(multiproc())


if __name__ == "__main__":
    asyncio.run(main)

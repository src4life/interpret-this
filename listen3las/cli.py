from listen3las import ConnectionSettings, WSBridge
from loguru import logger
import time
import typer


def main(
    translation_server: str = typer.Option(
        ..., envvar="TRANSLATION_SERVER", help="The host delivering audio from the 3LAS stream. Something like ws://3las-host:9603"
    ),
    rtmp_input: str = typer.Option(..., envvar="RTMP_INPUT", help="The incoming rtmp stream to mux the audio with"),
    rtmp_output: str = typer.Option(
         ..., envvar="RTMP_OUTPUT", help="The outgoing rtmp stream something like rtmp://stream-host:8080/live"
    ),
    auto_restart: bool = False,
):

    conn_settings = ConnectionSettings(
        translation_server=translation_server,
        rtmp_input=rtmp_input,
        rtmp_output=rtmp_output,
    )

    logger.info(conn_settings)

    while True:
        wsbridge = WSBridge(connection_settings=conn_settings)
        wsbridge.run()
        if not auto_restart:
            break
        logger.info("Websocket closed or could not connect, restarting soon...")
        time.sleep(5)


def cli():
    typer.run(main)


if __name__ == "__main__":
    main(auto_restart=True)

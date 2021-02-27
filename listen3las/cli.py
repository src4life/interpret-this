from listen3las import ConnectionSettings, WSBridge, LasInterpreterSink, las_interpreter_sink
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
        rtmp_input=rtmp_input,
        rtmp_output=rtmp_output,
    )

    logger.info(conn_settings)

    while True:
        las_sink = LasInterpreterSink(translation_server)
        wsbridge = WSBridge(interpreter_sink=las_sink, connection_settings=conn_settings)
        wsbridge.run()
        if not auto_restart:
            break
        logger.info("Websocket closed or could not connect, restarting soon...")
        time.sleep(5)


def cli():
    typer.run(main)


if __name__ == "__main__":
    main(auto_restart=True)

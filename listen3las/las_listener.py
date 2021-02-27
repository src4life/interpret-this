import websocket
import subprocess
from dataclasses import dataclass
from loguru import logger

@dataclass
class EncodeSettings:
    transcode_delay: float = 0.0

    compressor_threshold: float = 0.01
    compressor_ratio: float = 5.0
    compressor_release: float = 3000.0
    compressor_attack: float = 1.0
    compressor_weight: int = 1
    interpreter_weight: int = 1

    def to_ffmpeg_filter(self) -> str:
        return f"[1:a]loudnorm,adelay={self.transcode_delay}|{self.transcode_delay},asplit[sc][tnorm]; \
            [0:a][sc]sidechaincompress=threshold={self.compressor_threshold}:ratio={self.compressor_ratio}: \
            release={self.compressor_release}:attack={self.compressor_attack}[compout]; \
            [compout][tnorm]amix=weights={self.compressor_weight} {self.interpreter_weight}"


@dataclass
class ConnectionSettings:
    translation_server: str = "ws://localhost"
    rtmp_input: str = "rtmp://localhost:9191/live"
    rtmp_output: str = "rtmp://localhost:8080/live"


class WSBridge:
    def __init__(
        self,
        connection_settings: ConnectionSettings,
        encoder_settings: EncodeSettings = None,
    ) -> None:
        self.process = None
        self.encoder_settings = encoder_settings
        if self.encoder_settings is None:
            self.encoder_settings = EncodeSettings()
        self.connection_settings = connection_settings

        self.ws = websocket.WebSocketApp(
            f"{self.connection_settings.translation_server}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
        )

    def on_message(self, message):
        logger.info("recv msg")
        #s_out, s_err = self.process.communicate(message, timeout=1)
        self.process.stdin.write(message)
        self.process.stdin.flush()
        #logger.info(s_out)
        #logger.info(s_err)

    def on_error(self, ws, error):
        logger.error(error)

    def on_open(self, ws):
        logger.info("Translator connection open")

    def on_close(self):
        self.process.terminate()

    def run(self):
        args = [
            "ffmpeg",
            "-f",
            "flv",
            "-thread_queue_size",
            "1024",
            "-i",
            self.connection_settings.rtmp_input,
            "-c:v",
            "copy",
            "-f",
            "mp3",
            "-thread_queue_size",
            "1024",
            "-i",
            "pipe:0",
            "-c:a",
            "aac",
            "-filter_complex",
            self.encoder_settings.to_ffmpeg_filter(),
            "-f",
            "flv",
            self.connection_settings.rtmp_output,
        ]
        self.process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(" ".join(self.process.args))

        logger.info("Starting websocket client")
        self.ws.run_forever(ping_interval=5, ping_timeout=2)

        logger.info("Websocket client closed")

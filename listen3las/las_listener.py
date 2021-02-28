import subprocess
from dataclasses import dataclass
from loguru import logger
from threading import Thread

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
    rtmp_input: str = "rtmp://localhost:9191/live"
    rtmp_output: str = "rtmp://localhost:8080/live"

class InterpreterSink:
    def __init__(self) -> None:
       self.on_open = None
       self.on_close = None
       self.on_error = None
       self.on_data = None

    def set_cb(self, on_open, on_close, on_error, on_data) -> None:
        self.on_open = on_open
        self.on_close = on_close
        self.on_error = on_error
        self.on_data = on_data

    def run(self):
        pass

    def terminate(self):
        pass

class WSBridge:
    def __init__(
        self,
        interpreter_sink: InterpreterSink,
        connection_settings: ConnectionSettings,
        encoder_settings: EncodeSettings = None
    ) -> None:
        self.process = None
        self.encoder_settings = encoder_settings
        if self.encoder_settings is None:
            self.encoder_settings = EncodeSettings()
        self.connection_settings = connection_settings

        self.interpreter_sink = interpreter_sink
        self.interpreter_sink.set_cb(
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
        )

    def output_logger(self, pipe, output):
        for line in iter(pipe.readline, b''):
            output(line.decode('utf-8'))

    def on_data(self, data):
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def on_error(self, error):
        logger.error(error)

    def on_open(self):
        logger.info("Interpreter sink open")

    def on_close(self):
        logger.info("Interpreter sink closed")
        self.process.kill()

    def run(self):
        args = [
            "ffmpeg",
            "-f",
            "flv",
            "-thread_queue_size",
            "1024",
            "-i",
            self.connection_settings.rtmp_input,
            "-f",
            "mp3",
            "-thread_queue_size",
            "1024",
            "-i",
            "pipe:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-q:a",
            "2",
            "-ac",
            "2",
            "-filter_complex",
            self.encoder_settings.to_ffmpeg_filter(),
            "-f",
            "flv",
            self.connection_settings.rtmp_output,
        ]
        self.process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # FFmpeg logs to stderr, so listen to this but output as info.
        ffmpeg_logger = Thread(target=self.output_logger, args=(self.process.stderr,logger.info,))
        ffmpeg_logger.start()

        logger.info(" ".join(self.process.args))
        logger.info("Starting interpreter sink")
        self.process.wait()
        self.interpreter_sink.run()
        ffmpeg_logger.join()

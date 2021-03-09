from listen3las import InterpreterSink
import websocket

class LasInterpreterSink(InterpreterSink):
    def __init__(self, las_host: str) -> None:
        super().__init__()
        self.las_host = las_host
        self.ws = websocket.WebSocketApp(
            las_host,
            on_message = lambda ws, message: self._ws_on_message(ws, message),
            on_error = lambda ws, error: self._ws_on_error(ws, error),
            on_open = lambda ws: self._ws_on_open(ws),
            on_close = lambda ws: self._ws_on_close(ws)
        )

    def _ws_on_message(self, ws, message):
        if self.on_data is not None:
            self.on_data(message)

    def _ws_on_error(self, ws, error):
        if self.on_error is not None:
            self.on_error(error)

    def _ws_on_open(self, ws):
        if self.on_open is not None:
            self.on_open()

    def _ws_on_close(self, ws):
        if self.on_close is not None:
            self.on_close()

    def run(self):
        self.ws.run_forever(ping_interval=5, ping_timeout=2)

    def terminate(self):
        self.ws.close()

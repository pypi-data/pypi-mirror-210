from http.server import HTTPServer, BaseHTTPRequestHandler
from ValiotWorker.Logging import LogLevel

# TODO: Add this attribute to the class
log_callback = None


class HealthServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        global log_callback
        if log_callback:
            log_callback(LogLevel.DEBUG, "KeepAlive")
        self._set_headers()
        self.wfile.write(self._html("Alive!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))

    def log_message(self, format, *args):
        return


def run(logger_callback, server_class=HTTPServer, handler_class=HealthServer, addr="localhost", port=8000):
    global log_callback
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    log_callback = logger_callback

    log_callback(LogLevel.SUCCESS,
                 "Health Server started at {} -> {} ...".format(addr, port))

    httpd.serve_forever()

from http.server import HTTPServer, SimpleHTTPRequestHandler
from contextlib import contextmanager
from threading import Thread
import os
import tempfile

class CSPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # self.send_header('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plaid.com ;")
        super().end_headers()

    def translate_path(self, path):
        # Serve files from the specified directory without changing global working directory
        if self.directory:
            return os.path.join(self.directory, path.lstrip('/'))
        return super().translate_path(path)


@contextmanager
def run_link_http_server(link_token: str):
    with tempfile.TemporaryDirectory() as serve_directory:
        _generate_auth_page(link_token, os.path.join(serve_directory, 'index.html'))
        handler = lambda *args, **kwargs: CSPRequestHandler(*args, directory=serve_directory, **kwargs)
        httpd = HTTPServer(('localhost', 8000), handler)
        server_thread = Thread(target=httpd.serve_forever)
        server_thread.start()
        try:
            yield "http://localhost:8000"
        finally:
            httpd.shutdown()
            server_thread.join()


def _generate_auth_page(link_token: str, file_path: str):
    page = """
        <html>
            <body>
                <button id='linkButton'>Open Link - Institution Select</button>
                <p id="results"></p>
                <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
                <script>
                    var linkHandler = Plaid.create({
                        token: '""" + link_token + """',
                        onLoad: function() {
                            // The Link module finished loading.
                        },
                        onSuccess: function(public_token, metadata) {
                            // Send the public_token to your app server here.
                            // The metadata object contains info about the institution the
                            // user selected and the account ID, if selectAccount is enabled.
                            console.log('public_token: '+public_token+', metadata: '+JSON.stringify(metadata));
                            document.getElementById("results").innerHTML = "public_token: " + public_token + "<br>metadata: " + JSON.stringify(metadata);
                        },
                        onExit: function(err, metadata) {
                            // The user exited the Link flow.
                            if (err != null) {
                                // The user encountered a Plaid API error prior to exiting.
                            }
                            // metadata contains information about the institution
                            // that the user selected and the most recent API request IDs.
                            // Storing this information can be helpful for support.
                        }
                    });

                    // Trigger the standard institution select view
                    document.getElementById('linkButton').onclick = function() {
                        linkHandler.open();
                    };
                </script>
            </body>
        </html>
    """

    f = open(file_path, mode='w')
    f.write(page)
    f.close()
from textual_serve.server import Server

server = Server("PYTHONPATH=. python src/tui/app.py")
server.serve()

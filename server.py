from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
	#Handle HTTP requests by returning a fixed 'page'

	#page to send back
	Page = '''\
		<html>
		<body>
		<p>Hello web!</p>
		</body>
		</html>
	'''

	#handle get request
	def do_GET(self):
		print('self page', self.Page)
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", str(len(self.Page)))
		self.end_headers()
		self.wfile.write(self.Page.encode("utf-8"))


if __name__ == '__main__':
	serverAddress = ('', 8080)
	server = HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()
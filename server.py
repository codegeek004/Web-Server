from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
	#Handle HTTP requests by returning a fixed 'page'

	#page to send back
	Page = '''\
		<html>
		<body>
		<table>
		<tr>  <td>Header</td>         <td>Value</td>          </tr>
		<tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
		<tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
		<tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
		<tr>  <td>Command</td>        <td>{command}</td>      </tr>
		<tr>  <td>Path</td>           <td>{path}</td>         </tr>
		</table>
		</body>
		</html>
	'''

	Error_Page = '''
		<html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{e}</p>
        </body>
        </html>
	'''

	#handle get request
	def do_GET(self):
		try:
			#figure out what is requested exactly
			full_path = os.getcwd() + self.path 

			#if path does not exist
			if not os.path.exists(full_path):
				raise ServerException(" '{0}' not found".format(self.path))

			#if there is a file
			elif os.path.isfile(full_path):
				self.handle_file(full_path)

			else:
				raise ServerException("Unknown Exception '{0}'".format(self.path))

		except Exception as e:
			self.handle_error(e)

	def handle_file(self, full_path):
		try:
			with open(full_path, 'rb') as reader:
				content = reader.read()
			self.send_content(content)
		except IOError as e:
			e = "'{0}' cannot be read: {1}".format(self.path, e)
			self.handle_error(e)	

	#handle unknown errors
	def handle_error(self, e):
		content = self.Error_Page.format(path=self.path, e=e)
		self.send_content(content, 404)

	def send_content(self, content, status=200):
		self.send_response(status)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", str(len(content)))
		self.end_headers()
		self.wfile.write(content.encode('utf-8'))



	def create_page(self):
		values = {
			'date_time' : self.date_time_string(),
			'client_host' : self.client_address[0],
			'client_port' : self.client_address[1],
			'command' : self.command,
			'path' : self.path
		}
		print('values', values)
		print('page ke upar')
		page = self.Page.format(**values)
		print('page', page)
		return page

	def send_page(self, page):
		self.send_response(200)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", str(len(page)))
		self.end_headers()
		self.wfile.write(page.encode('utf-8'))


if __name__ == '__main__':
	serverAddress = ('', 8080)
	server = HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()
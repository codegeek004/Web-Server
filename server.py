import subprocess
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class ServerException(Exception):
	"""Custom exception for server errors."""
	pass


class case_no_file:
	"""File or directory does not exist."""

	def test(self, handler):
		return not os.path.exists(handler.full_path)

	def act(self, handler):
		raise ServerException(f"'{handler.path}' does not exist")


class case_always_fail:
	"""Base case if nothing else worked."""

	def test(self, handler):
		return True

	def act(self, handler):
		raise ServerException(f"Unknown object '{handler.path}'")


class case_directory_index_file:
	"""Serve index.html page for a directory."""

	def index_path(self, handler):
		return os.path.join(handler.full_path, 'index.html')

	def test(self, handler):
		return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

	def act(self, handler):
		handler.handle_file(self.index_path(handler))


class case_directory_index_no_file:
	"""Serve listing for a directory without an index.html page."""

	def test(self, handler):
		return os.path.isdir(handler.full_path) and not os.path.isfile(
			os.path.join(handler.full_path, 'index.html')
		)

	def act(self, handler):
		handler.list_dir(handler.full_path)


class case_cgi_file:
	"""Something runnable."""

	def test(self, handler):
		return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

	def act(self, handler):
		handler.run_cgi(handler.full_path)


class case_existing_file:
	"""File exists."""

	def test(self, handler):
		return os.path.isfile(handler.full_path)

	def act(self, handler):
		handler.handle_file(handler.full_path)


class RequestHandler(BaseHTTPRequestHandler):
	"""Handle HTTP requests."""

	Cases = [
		case_no_file(),
		case_existing_file(),
		case_cgi_file(),
		case_directory_index_file(),
		case_directory_index_no_file(),
		case_always_fail(),
	]

	Error_Page = '''
		<html>
		<body>
		<h1>Error accessing {path}</h1>
		<p>{e}</p>
		</body>
		</html>
	'''

	Listing_Page = '''\
		<html>
		<body>
		<ul>
		{0}
		</ul>
		</body>
		</html>
	'''

	def do_GET(self):
		try:
			# Define the full path to the requested file
			self.full_path = os.getcwd() + self.path

			# Check if it’s a valid Python script or file
			for case in self.Cases:
				if case.test(self):
					case.act(self)
					break
		except Exception as e:
			self.handle_error(str(e))

	def run_cgi(self, script_path):
		"""Run the Python script securely and send the output."""
		try:
			# Run the Python script using subprocess
			process = subprocess.Popen(
				['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
			)
			stdout, stderr = process.communicate()

			if process.returncode != 0:
				# If there's an error in the script, return the error
				self.handle_error(f"Error running script: {stderr.decode()}")
			else:
				# Otherwise, send the output of the script
				self.send_content(stdout.decode(), 200)
		except Exception as e:
			self.handle_error(f"Error running CGI script: {str(e)}")


	def handle_file(self, full_path):
		"""Handle file request and send content."""
		try:
			with open(full_path, 'rb') as reader:
				content = reader.read()
			self.send_content(content)
		except IOError as e:
			self.handle_error(f"'{full_path}' cannot be read: {e}")

	def handle_error(self, e):
		"""Send error message as an HTTP response."""
		content = self.Error_Page.format(path=self.path, e=e)
		self.send_content(content, 404)

	def list_dir(self, full_path):
		"""Handle directory listing."""
		try:
			entries = os.listdir(full_path)
			bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
			page = self.Listing_Page.format('\n'.join(bullets))
			self.send_content(page)
		except OSError as msg:
			msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
			self.handle_error(msg)

	def send_content(self, content, status=200):
		"""Send content as an HTTP response."""
		self.send_response(status)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", str(len(content)))
		self.end_headers()
		if isinstance(content, bytes):
			self.wfile.write(content)
		else:
			self.wfile.write(content.encode('utf-8'))


if __name__ == '__main__':
	# Start the server on localhost:8080
	serverAddress = ('', 8080)
	server = HTTPServer(serverAddress, RequestHandler)
	print("Server started on http://localhost:8080")
	server.serve_forever()

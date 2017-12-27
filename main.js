// load the http module to create an http server
var http = require('http');

// Configure out HTTP server to respond request
var server = http.createServer(function (request, response) {
	response.writeHead(200, {"Content-Type": "text/plain"});
	response.end("Hello\n");
});

// Listion on port 8000, IP defaults to 127.0.0.1
server.listen(8000);

console.log("Server running at http://127.0.0.1:8000");

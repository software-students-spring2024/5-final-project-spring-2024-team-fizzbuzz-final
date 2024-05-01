document.addEventListener('DOMContentLoaded', main);

function main() {
    let socket = io.connect('/waiting');

    socket.on('connect', function() {
        console.log('Websocket has connected to the server!');
    });

    socket.on('ready', function(data) {
        console.log(data.message);
        socket.close()
        window.location.replace('/play');
    });
};
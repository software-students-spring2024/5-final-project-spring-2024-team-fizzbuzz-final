document.addEventListener('DOMContentLoaded', main);

function main() {
    let socket = io.connect('/waiting', {transports: ['websocket']});

    socket.on('connect', function() {
        console.log('Websocket has connected to the server!');
    });

    socket.on('ready', function(data) {
        console.log(data.message);

        window.location.replace('/play');
    });
};
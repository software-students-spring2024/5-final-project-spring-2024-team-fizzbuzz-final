document.addEventListener('DOMContentLoaded', main);

function main() {
    let socket = io.connect('/waiting');
    let assigned;

    socket.on('connect', function() {
        console.log('Websocket has connected to the server!');
    });

    socket.on('assigned-room', function(data) {
        console.log(data);
        assigned = data["room"];
    })

    socket.on('ready', function(data) {
        console.log(data.message);
        if (assigned == data["room"]) {
            window.location.replace('/play');
        }
    });
};

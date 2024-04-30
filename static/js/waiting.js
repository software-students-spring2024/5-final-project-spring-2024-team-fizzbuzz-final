let socket = io.connect('/waiting');
let assigned;

socket.on('connect', function(message) {
    console.log('Websocket has connected to the server!');
    console.log(message);
});

socket.on('assigned-room', function(data) {
    console.log(data);
    assigned = data["room"];
})

socket.on('ready', function(data) {
    console.log(data);
    console.log(assigned);
    console.log(data["room"]);
    if (assigned == data["room"]) {
        console.log("Lezzgpooo")
        window.location.replace('/play');
    }
});

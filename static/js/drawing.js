let socket = io.connect('/play');
let isDrawing = false;
let lastX, lastY;
let path = null;

socket.on('connect', function() {
    console.log('Websocket has connected to the server!');

});

socket.on('canvas_cleared', function() {
    canvas.clear();
});

socket.on('drawing', function(data) {
    let receivedPath = new fabric.Path(data.path, {
        fill: null,
        stroke: 'black',
        strokeWidth: 2,
        selectable: false
    });
    canvas.add(receivedPath);
    canvas.renderAll();
});

const canvas = new fabric.Canvas('gameCanvas', {
    isDrawingMode: true 
});

canvas.setDimensions({ width: 800, height: 400 });

const clearButton = document.getElementById('clearButton');

clearButton.addEventListener('click', function() {

    canvas.clear();
    socket.emit('canvas_cleared');
});

// keeps track of the mouse's most recent position
canvas.on('mouse:down', function(options) {
    isDrawing = true;
    // use the canvas's getPointer method to get the x and y coordinates of the mouse
    const pointer = canvas.getPointer(options.e);

    // create a path starting at the x and y coords of the mouse
    path = new fabric.Path(`M ${pointer.x} ${pointer.y}`, {
        fill: null,
        stroke: 'black',
        strokeWidth: 2,
        selectable: false,
        
    
        });
    
    // add the path to the canvas
    canvas.add(path);

    
    // log that the mouse has been pressed down
    console.log('Mouse down at coordinates:', pointer.x, pointer.y);
});

// when the mouse is moving, use the socket to emit the x and y coordinates to the server
canvas.on('mouse:move', function(options) {
    if (!isDrawing || !path ) return;
    // use the canvas's getPointer method to get the x and y coordinates of the mouse
    const pointer = canvas.getPointer(options.e);
    // add points to the path as the mouse moves
    path.path.push(['L', pointer.x, pointer.y]);

    //render the canvas
    canvas.renderAll();

    // emit the x and y coordinates of the mouse to the server
    socket.emit('drawing', { path: path.path });

    

});

canvas.on('mouse:up', function(options) {

    // if a path exists, set the coordinates of the path to the canvas and set the path to null using the setCoords method
    // the setCoords method updates the coordinates of the path and sets the path to null
    if (path) {
        path.setCoords();
    }

    isDrawing = false;

});

canvas.on('mouse:out', function() {
    isDrawing = false;
    path = null;
});


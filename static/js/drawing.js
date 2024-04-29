
const canvas = new fabric.Canvas('gameCanvas', {
    isDrawingMode: true 
});

canvas.setDimensions({ width: 800, height: 400 });

const clearButton = document.getElementById('clearButton');

clearButton.addEventListener('click', function() {

    canvas.clear();
});



canvas.on('mouse:down', function(options) {
    
    const pointer = canvas.getPointer(options.e);
    const x = pointer.x;
    const y = pointer.y;
    console.log('Mouse down at coordinates:', x, y);
});


// Function to draw on the canvas
function draw(x, y) {
    if (!isDrawing) return;

    if (!lastX || !lastY) {
        lastX = x;
        lastY = y;
    }

    const line = new fabric.Line([lastX, lastY, x, y], {
        fill: 'black',
        stroke: 'black',
        strokeWidth: 2,
        selectable: true,
    });
    canvas.add(line);
    canvas.renderAll();

    lastX = x;
    lastY = y;
}

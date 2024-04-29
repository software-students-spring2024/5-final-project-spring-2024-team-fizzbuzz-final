
const canvas = new fabric.Canvas('gameCanvas', {
    isDrawingMode: true 
});

canvas.setDimensions({ width: 800, height: 400 });



canvas.on('mouse:down', function(options) {
    
    const pointer = canvas.getPointer(options.e);
    const x = pointer.x;
    const y = pointer.y;
    console.log('Mouse down at coordinates:', x, y);
});

canvas.on('mouse:move', function(options) {
   
    // if (options.e.buttons === 1) {
    //     const pointer = canvas.getPointer(options.e);
    //     const x = pointer.x;
    //     const y = pointer.y;
    //     console.log('Mouse move at coordinates:', x, y);
    //     draw(x, y);
    // }
});

canvas.on('mouse:up', function(options) {
    // Handle mouse up event
    console.log('Mouse up');
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

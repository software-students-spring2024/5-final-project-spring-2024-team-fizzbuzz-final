// when the page is loaded, this function will be called
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    // when the user clicks the submit button, this function gets the value emits it to the server and clears the input field
    document.getElementById("guess-form").addEventListener("submit", function(event) {
        event.preventDefault();
        const guess = document.getElementById("guess-input").value;
        socket.emit('submit_guess', { guess: guess });
        document.getElementById('guess-input').value = '';  
    });

    socket.on("guess", function(data) {
        // Display whether the guess was correct or not
        const resultElement = document.getElementById('result');
        resultElement.textContent = data.message;
        resultElement.style.display = 'block';
    });


});
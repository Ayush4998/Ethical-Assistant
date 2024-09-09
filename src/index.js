import './index.css';
import reportWebVitals from './reportWebVitals';

// Ensure that DOM content is fully loaded before selecting elements
document.addEventListener("DOMContentLoaded", function () {
  // Select necessary DOM elements
  const inputField = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const messageArea = document.getElementById("message-area");

  // Function to append message to the conversation area
  function appendMessage(sender, text) {
    const messageDiv = document.createElement("div");

    // Add classes based on sender (user or bot)
    if (sender === "You") {
      messageDiv.classList.add("message", "user-message");
    } else {
      messageDiv.classList.add("message", "bot-message");
    }

    const messageText = document.createElement("p");
    messageText.textContent = text;

    messageDiv.appendChild(messageText);
    messageArea.appendChild(messageDiv);

    // Automatically scroll to the latest message
    messageArea.scrollTop = messageArea.scrollHeight;
  }

  // Append initial bot message
  appendMessage("Bot", "Welcome! I am your ethical assistant. How can I assist you today?");

  // Function to handle user input
  function handleUserInput() {
    const userInput = inputField.value.trim();

    if (userInput !== "") {
      // Append the user's message
      appendMessage("You", userInput);

      // Clear input field
      inputField.value = "";

      // Send user input to Flask API and get bot response
      fetch('http://127.0.0.1:5000/api/decision', {  // Assuming /api/decision is the correct endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),  // Send user message to Flask
      })
        .then(response => response.json())
        .then(data => {
          // Append bot response from Flask API
          appendMessage("Bot", data.bot_response || "Sorry, I couldn't process that.");
        })
        .catch(error => {
          console.error('Error:', error);
          appendMessage("Bot", "Sorry, there was an error.");
        });
    }
  }

  // Add event listeners for send button and Enter key press
  sendButton.addEventListener("click", handleUserInput);

  inputField.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      handleUserInput();
    }
  });
});

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

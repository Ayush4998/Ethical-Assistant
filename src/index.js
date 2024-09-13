import './index.css';
import reportWebVitals from './reportWebVitals';

document.addEventListener("DOMContentLoaded", () => {
  const inputField = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const messageArea = document.getElementById("message-area");
  scrollToBottom()
  // Function to append messages to the chat area
  function appendMessage(sender, text) {
    const messageDiv = document.createElement("div");
    const messageText = document.createElement("p");
    messageText.textContent = text;
    messageDiv.appendChild(messageText);

    if (sender === "You") {
      messageDiv.classList.add("message", "user-message");
    } else {
      messageDiv.classList.add("message", "bot-message");
    }

    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight;  // Scroll to the bottom after appending
  }

  // Function to handle user input
  function handleUserInput() {
    const userInput = inputField.value.trim();

    if (userInput !== "") {
      appendMessage("You", userInput);  // Show user message
      
      inputField.value = "";  // Clear input field

      // Send the user message to the Flask API
      fetch('http://127.0.0.1:5000/api/decision', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),  // Send the user input to the API
        
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // Parse JSON response
      })
      .then(data => {
        // Append the bot's response or error message if no response
        appendMessage("Bot", data.bot_response || "Sorry, I couldn't process that.");
      })
      .catch(error => {
        console.error('Error:', error);
        appendMessage("Bot", "Sorry, there was an error processing your request.");
      });
    }
  }
  /* Trigger auto-scroll on new message */
  function scrollToBottom() {
    const conversationArea = document.querySelector('.conversation-area');
    conversationArea.scrollTop = conversationArea.scrollHeight;
  }
  // Function to initiate the conversation
  function startConversation() {
    appendMessage("Bot", "Welcome! I am your ethical assistant. How can I assist you today?");
  }

  // Event listeners for button click and Enter key press
  sendButton.addEventListener("click", handleUserInput);
  
  inputField.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      handleUserInput();
    }
  });

  // Start the conversation when the page loads
  startConversation();
});

// If you want to measure performance in your app, pass a function to log results
reportWebVitals();

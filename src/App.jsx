import { useRef, useState } from "react";
import ChatbotIcon from "./components/ChatbotIcon";
import ChatForm from "./components/ChatForm";
import ChatMessage from "./components/ChatMessage";
import { useEffect } from "react";
import { companyInfo } from "./components/companyInfo";

const App = () => {
  const [chatHistory, setChatHistory] = useState([
    {
      hideInChat: true,
      role: "model",
      text: companyInfo,
    },
  ]);
  const [showChatbot, setShowChatbot] = useState(false);
  const chatBodyRef = useRef();

  const generateBotResponse = async (history) => {
    // Helper function to update chat history
    const updateHistory = (text, isError = false) => {
      setChatHistory((prev) => [
        ...prev.filter((msg) => msg.text !== "Thinking..."),
        { role: "model", text, isError },
      ]);
    };

    //Format chat history for the API request
    history = history.map(({ role, text }) => ({ role, parts: [{ text }] }));

    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: history }),
    };

    const maxRetries = 3; // Set a maximum number of retries
    let retries = 0;

    while (retries < maxRetries) {
      try {
        // Make the API call to get the bot's response
        const response = await fetch(
          import.meta.env.VITE_API_URL,
          requestOptions
        );

        if (response.status === 503) {
          // If it's a 503 error, wait and retry
          retries++;
          console.warn(
            `503 Service Unavailable. Retrying... Attempt ${retries}`
          );
          await new Promise((resolve) => setTimeout(resolve, 1000 * retries)); // Wait longer on subsequent retries
          continue; // Skip to the next iteration of the loop
        }

        const data = await response.json();
        if (!response.ok)
          throw new Error(data.error.message || "Something went wrong");

        // Clean and update chat history with the bot's response
        const apiResonseText = data.candidates[0].content.parts[0].text
          .replace(/\*\*(.*?)\*\*/g, "$1")
          .trim();
        updateHistory(apiResonseText);
        break; // Exit the loop on success
      } catch (error) {
        if (
          retries === maxRetries - 1 ||
          error.message !== "Something went wrong"
        ) {
          // If max retries reached or it's not a generic error, update history with the error
          updateHistory(error.message, true);
          break; // Exit the loop after handling the error
        }
        retries++;
        console.warn(`Error fetching response. Retrying... Attempt ${retries}`);
        await new Promise((resolve) => setTimeout(resolve, 1000 * retries)); // Wait longer on subsequent retries
      }
    }

    if (retries === maxRetries) {
      updateHistory(
        "Service is currently unavailable. Please try again later.",
        true
      );
    }
  };

  useEffect(() => {
    // Auto-scroll whenever chat history updates
    chatBodyRef.current.scrollTo({
      top: chatBodyRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [chatHistory]);

  return (
    <div className={`container ${showChatbot ? "show-chatbot" : ""}`}>
      <button
        onClick={() => setShowChatbot((prev) => !prev)}
        id="chatbot-toggler"
      >
        <span className="material-symbols-outlined">mode_comment</span>
        <span className="material-symbols-outlined">close</span>
      </button>

      <div className="chatbot-popup">
        {/* Chatbot Header */}
        <div className="chat-header">
          <div className="header-info">
            <ChatbotIcon />
            <h2 className="logo-text">LawStand AI ⚖️</h2>
          </div>
          <button
            onClick={() => setShowChatbot((prev) => !prev)}
            className="material-symbols-outlined"
          >
            keyboard_arrow_down
          </button>
        </div>
        {/* Chatbot Body */}
        <div ref={chatBodyRef} className="chat-body">
          <div className="message bot-message">
            <ChatbotIcon />
            <p className="message-text">
              Welcome to LawStand AI ⚖️. <br />I provide information synthesized
              from reliable legal sources. Please note that my answers are for
              informational purposes only. <br />
              What topic can I assist you with today?
            </p>
          </div>

          {/* Render the chat history dynamically */}
          {chatHistory.map((chat, index) => (
            <ChatMessage key={index} chat={chat} />
          ))}
        </div>

        {/* Chatbot Footer */}
        <div className="chat-footer">
          <ChatForm
            chatHistory={chatHistory}
            setChatHistory={setChatHistory}
            generateBotResponse={generateBotResponse}
          />
        </div>
      </div>
    </div>
  );
};

export default App;

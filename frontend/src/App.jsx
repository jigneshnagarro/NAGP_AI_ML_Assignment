import { useState } from "react";
import ChatMessage from "./components/ChatMessage";
import "./App.css";


function App() {

  const [sessionId] = useState(
    () => crypto.randomUUID()
  );


  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I am your Singapore travel assistant. I can help with attractions, transportation, food, itineraries, current weather and currency conversion.",
      tools_used: [],
      sources: [],
      mcp_used: false
    }
  ]);


  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);


  const sendMessage = async () => {

    if (!input.trim() || loading) {
      return;
    }


    const question = input.trim();


    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: question
      }
    ]);


    setInput("");
    setLoading(true);


    try {

      const response = await fetch(
        "http://localhost:8000/api/chat",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            session_id: sessionId,
            question: question
          })
        }
      );


      if (!response.ok) {
        throw new Error("API request failed");
      }


      const data = await response.json();


      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer[0].text,
          tools_used: data.tools_used || [],
          sources: data.sources || [],
          mcp_used: data.mcp_used || false
        }
      ]);


    } catch (error) {

      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I could not connect to the travel assistant backend.",
          tools_used: [],
          sources: [],
          mcp_used: false
        }
      ]);


    } finally {

      setLoading(false);

    }
  };


  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();

    }
  };


  const clearChat = () => {

    window.location.reload();

  };


  return (

    <div className="app">

      <header className="header">

        <div className="header-content">

          <div className="header-title">

            <h1>
              Singapore Travel Assistant
            </h1>

          </div>


          <button
            className="clear-button"
            onClick={clearChat}
          >
            New Chat
          </button>

        </div>

      </header>


      <main className="chat-container">

        <div className="messages">

          {messages.map((message, index) => (

            <ChatMessage
              key={index}
              message={message}
            />

          ))}


          {loading && (

            <div className="message-wrapper assistant-message">

              <div className="message-label">
                Travel Assistant
              </div>

              <div className="message-content typing">
                Thinking...
              </div>

            </div>

          )}

        </div>


        <div className="input-container">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about Singapore..."
            rows={2}
            disabled={loading}
          />


          <button
            onClick={sendMessage}
            disabled={
              loading ||
              !input.trim()
            }
          >
            Send
          </button>

        </div>


        <div className="footer-note">

          

        </div>

      </main>

    </div>

  );
}


export default App;
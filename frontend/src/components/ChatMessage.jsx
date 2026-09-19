import Markdown from 'react-markdown'
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-wrapper ${
        isUser ? "user-message" : "assistant-message"
      }`}
    >
      <div className="message-label">
        {isUser ? "You" : "Travel Assistant"}
      </div>

      <div className="message-content">
        <Markdown remarkPlugins={[remarkGfm, remarkBreaks]}>
          {message.content}
        </Markdown>
      </div>

      {!isUser && message.tools_used?.length > 0 && (
        <div className="tool-section">

          {message.tools_used.map((tool) => (
            <span
              className="tool-badge"
              key={tool}
            >
              {tool === "search_singapore_knowledge"
                ? "Knowledge Base"
                : tool === "get_singapore_weather"
                ? "Weather MCP"
                : tool === "convert_inr_to_sgd"
                ? "Currency MCP"
                : tool}
            </span>
          ))}

        </div>
      )}

      {!isUser && message.sources?.length > 0 && (
        <div className="sources">

          <div className="sources-title">
            Sources
          </div>

          {message.sources.map((source, index) => (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="source-card"
            >
              {source.title}
            </a>
          ))}

        </div>
      )}

      {!isUser && message.mcp_used && (
        <div className="mcp-info">
          Current information retrieved using MCP
        </div>
      )}

    </div>
  );
}

export default ChatMessage;
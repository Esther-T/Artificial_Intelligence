import { useState } from "react";
import { sendMessage, generateImage } from "./api";

function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [imageUrl, setImageUrl] = useState(null);

  const handleChat = async () => {
    const userMsg = { role: "user", content: input };
    setMessages([...messages, userMsg]);

    const res = await sendMessage(input);
    setMessages(prev => [...prev, { role: "ai", content: res.reply }]);
    setInput("");
  };

  const handleImage = async () => {
    const res = await generateImage(input);
    setImageUrl(res.image_url);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Kawaii Chatbot 🤖</h2>

      <div>
        {messages.map((m, i) => (
          <p key={i}><b>{m.role}:</b> {m.content}</p>
        ))}
      </div>

      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Type something..."
        style={{ width: "50%" }}
        rows={4}
      />
      <br/>
      <button onClick={handleChat}>Send</button>
      {/* <button onClick={handleImage}>Generate Image</button> */}

      {imageUrl && <img src={imageUrl} width="300" />}
    </div>
  );
}

export default Chatbot;

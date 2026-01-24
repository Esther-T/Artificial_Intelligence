import { useState } from "react";
import { sendMessage, generateImage } from "./api";
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';


function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [imageUrl, setImageUrl] = useState(null);

  const handleChat = async () => {
    const userMsg = { role: "you", content: input };
    setMessages([...messages, userMsg]);

    const res = await sendMessage(input);
    setMessages(prev => [...prev, { role: "shiro-bot 🤖", content: res.reply }]);
    setInput("");
  };

  const handleImage = async () => {
    const res = await generateImage(input);
    setImageUrl(res.image_url);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Shiro-Bot 🤖</h2>

      <div>
        {messages.map((m, i) => (
          <p key={i}><b>{m.role}:</b> {m.content}</p>
        ))}
      </div>
        <Form.Control as="textarea"         
          placeholder="Type something..."
          rows={4} 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          style={{ width: '100%' }}/>
      <Button onClick={handleChat} className="mt-2">
              Send
      </Button>
      {/* <button onClick={handleImage}>Generate Image</button> */}

      {imageUrl && <img src={imageUrl} width="300" />}
    </div>
  );
}

export default Chatbot;

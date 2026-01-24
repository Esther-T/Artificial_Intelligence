const API_BASE_URL = "http://localhost:8000";

export async function sendMessage(message) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  return response.json();
}

/**
 * Generate an image from a prompt
 * @param {string} prompt
 * @returns {Promise<{ image_url: string }>}
 */
export async function generateImage(prompt) {
  const response = await fetch(`${API_BASE_URL}/image`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate image");
  }

  return response.json();
}

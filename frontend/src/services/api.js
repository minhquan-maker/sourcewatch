import axios from "axios";

const api = axios.create({
  baseURL: "",
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

export async function analyzeUrl(url) {
  const response = await api.post("/analyze", { url });
  return response.data;
}

export async function analyzeUrlSSE(url, { onStage, onResult, onError }) {
  const response = await fetch("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || `Server error ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop(); // keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.stage === "error") {
            onError(data.message);
            return;
          }
          if (data.stage === "done" && data.result) {
            onResult(data.result);
            return;
          }
          // Progress stage update
          onStage(data.stage, data.message);
        } catch {
          // ignore parse errors
        }
      }
    }
  }
}

export async function healthCheck() {
  const response = await api.get("/health");
  return response.data;
}

export async function indexSources() {
  const response = await api.post("/index");
  return response.data;
}
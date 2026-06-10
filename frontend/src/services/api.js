import axios from "axios";

const api = axios.create({
  baseURL: "",
  timeout: 60000,
  headers: { "Content-Type": "application/json" },
});

export async function analyzeUrl(url) {
  const response = await api.post("/analyze", { url });
  return response.data;
}

export async function healthCheck() {
  const response = await api.get("/health");
  return response.data;
}

export async function indexSources() {
  const response = await api.post("/index");
  return response.data;
}

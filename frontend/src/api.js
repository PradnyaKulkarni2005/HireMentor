const BASE_URL = import.meta.env.VITE_API_URL || `http://127.0.0.1:8000`;
let sessionId = null;

const timeoutFetch = async (url, options = {}, timeout = 15000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms. Backend may be slow or unavailable.`);
    }
    throw error;
  }
};

const parseResponse = async (res) => {
  let response;
  try {
    response = await res.json();
  } catch (e) {
    const text = await res.text();
    throw new Error(`Unable to parse JSON response: ${text || e.message}`);
  }
  return response;
};

export const getQuestion = async (currentSessionId = null, category = null) => {
  const queryParams = new URLSearchParams();
  const queryId = currentSessionId ? currentSessionId : sessionId;

  if (queryId) queryParams.append("session_id", queryId);
  if (category) queryParams.append("category", category);

  const res = await timeoutFetch(`${BASE_URL}/api/v1/question${queryParams.toString() ? `?${queryParams.toString()}` : ""}`);

  const response = await parseResponse(res);

  if (!res.ok) {
    throw new Error(response.message || `HTTP ${res.status} - Failed to get question`);
  }

  if (response.status === "success") {
    if (response.data?.session_id) {
      sessionId = response.data.session_id;
    }
    return response.data;
  }

  throw new Error(response.message || "Failed to get question");
};

export const sendAnswer = async (answer, currentSessionId = null) => {
  const queryId = currentSessionId ? currentSessionId : sessionId;
  if (!queryId) {
    throw new Error("Session ID missing. Please reload the page and try again.");
  }

  const res = await timeoutFetch(`${BASE_URL}/api/v1/answer?session_id=${encodeURIComponent(queryId)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  const response = await parseResponse(res);

  if (!res.ok) {
    throw new Error(response.message || `HTTP ${res.status} - Failed to send answer`);
  }

  if (response.status === "success") {
    return response.data;
  }

  throw new Error(response.message || "Failed to send answer");
};

export const getCategories = async () => {
  const res = await timeoutFetch(`${BASE_URL}/api/v1/categories`);
  const response = await parseResponse(res);

  if (!res.ok) {
    throw new Error(response.message || `HTTP ${res.status} - Failed to get categories`);
  }

  if (response.status === "success") {
    return response.data.categories || [];
  }

  throw new Error(response.message || "Failed to get categories");
};

export const resetSession = async () => {
  if (!sessionId) {
    throw new Error("Session ID missing. Cannot reset session.");
  }

  const res = await fetch(`${BASE_URL}/api/v1/reset?session_id=${encodeURIComponent(sessionId)}`, {
    method: "POST",
  });
  const response = await res.json();

  if (response.status === "success") {
    return response.data;
  }

  throw new Error(response.message || "Failed to reset session");
};
import { useEffect, useRef, useState } from "react";
import { getCategories, getQuestion, sendAnswer } from "./api";
import "./Chat.css";

const LANDING_HIGHLIGHTS = [
  {
    title: "Real interview flow",
    description: "Pick a track, answer one question at a time, and keep momentum like a live round.",
  },
  {
    title: "Instant feedback",
    description: "See scoring, matched concepts, and missed talking points after each answer.",
  },
  {
    title: "Voice practice",
    description: "Speak your response naturally and let the app capture and submit it for you.",
  },
];

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState("idle");
  const [sessionId, setSessionId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Loading categories...");
  const [statusType, setStatusType] = useState("info");
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryError, setCategoryError] = useState(null);
  const [categoryLoading, setCategoryLoading] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [recognitionActive, setRecognitionActive] = useState(false);
  const [recognitionError, setRecognitionError] = useState(null);
  const recognitionRef = useRef(null);
  const initialLoadRef = useRef(false);
  const messagesEndRef = useRef(null);

  const showLanding = !selectedCategory;
  const showChatInput = Boolean(selectedCategory);
  const isSendingAnswer =
    loadingPhase === "text-answer" || loadingPhase === "voice-answer";
  const isVoiceSubmitting = loadingPhase === "voice-answer";
  const isLoadingQuestion = loadingPhase === "question";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loadingPhase]);

  useEffect(() => {
    if (initialLoadRef.current) {
      return;
    }

    initialLoadRef.current = true;
    loadCategories();
  }, []);

  const initializeSpeechRecognition = () => {
    if (recognitionRef.current) {
      return recognitionRef.current;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return null;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = async (event) => {
      const transcript = event?.results?.[0]?.[0]?.transcript?.trim();

      if (!transcript) {
        setRecognitionError("No speech detected. Please try again.");
        setStatusMessage("No speech detected.");
        setStatusType("error");
        setRecognitionActive(false);
        return;
      }

      setInput(transcript);
      setRecognitionActive(false);
      setStatusMessage("Voice captured. Sending your answer...");
      setStatusType("info");
      await sendAnswerText(transcript, "voice");
    };

    recognition.onerror = (event) => {
      setRecognitionError(`Speech recognition error: ${event.error}`);
      setStatusMessage(`Speech recognition error: ${event.error}`);
      setStatusType("error");
      setRecognitionActive(false);
    };

    recognition.onend = () => {
      setRecognitionActive(false);
    };

    recognition.onspeechend = () => {
      setRecognitionActive(false);
      recognition.stop();
    };

    recognitionRef.current = recognition;
    return recognition;
  };

  const loadCategories = async () => {
    try {
      setCategoryLoading(true);
      setCategoryError(null);
      setStatusMessage("Loading categories...");
      setStatusType("info");

      const categoryList = await getCategories();

      if (!Array.isArray(categoryList) || categoryList.length === 0) {
        setCategories([]);
        setStatusMessage("Categories unavailable. You can still start a general interview.");
        setStatusType("info");
        return;
      }

      setCategories(categoryList);
      setStatusMessage("Choose a category to begin.");
      setStatusType("success");
    } catch (error) {
      const rawMessage = error?.message || "Unable to load categories.";
      setCategoryError(rawMessage);
      setCategories([]);
      setStatusMessage(rawMessage);
      setStatusType("error");
    } finally {
      setCategoryLoading(false);
    }
  };

  const loadQuestion = async (categoryParam = selectedCategory) => {
    try {
      setLoading(true);
      setLoadingPhase("question");
      setStatusMessage("Loading question...");
      setStatusType("info");

      const data = await getQuestion(sessionId, categoryParam);

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      if (data.category) {
        setSelectedCategory(data.category);
      } else if (categoryParam) {
        setSelectedCategory(categoryParam);
      }

      if (!data.question) {
        throw new Error("Question data was empty.");
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.question,
          type: "question",
          timestamp: new Date(),
        },
      ]);

      setStatusMessage("Question ready.");
      setStatusType("success");
    } catch (error) {
      const rawMessage = error?.message || "Unable to load the next question.";
      const friendlyMessage = /fetch|network|failed to fetch|aborted|timeout/i.test(rawMessage)
        ? "Backend unreachable. Start the API at http://127.0.0.1:8000 and refresh."
        : rawMessage;

      setStatusMessage(friendlyMessage);
      setStatusType("error");
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: friendlyMessage,
          type: "error",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      setLoadingPhase("idle");
    }
  };

  const handleCategorySelect = async (category) => {
    setSelectedCategory(category);
    setSessionId(null);
    setMessages([]);
    setInput("");
    setCategoryError(null);
    setRecognitionError(null);
    setStatusMessage(`Loading ${category} questions...`);
    setStatusType("info");
    await loadQuestion(category);
  };

  const handleGeneralStart = async () => {
    setSelectedCategory("General");
    setSessionId(null);
    setMessages([]);
    setInput("");
    setCategoryError(null);
    setRecognitionError(null);
    setStatusMessage("Loading general interview questions...");
    setStatusType("info");
    await loadQuestion(null);
  };

  const handleMicClick = () => {
    if (!speechSupported) {
      setRecognitionError("Speech recognition is not supported in this browser.");
      setStatusMessage("Speech recognition is not supported in this browser.");
      setStatusType("error");
      return;
    }

    if (recognitionActive) {
      recognitionRef.current?.stop();
      setRecognitionActive(false);
      return;
    }

    const recognition = initializeSpeechRecognition();
    if (!recognition) {
      setRecognitionError("Speech recognition is not supported in this browser.");
      setStatusMessage("Speech recognition is not supported in this browser.");
      setStatusType("error");
      return;
    }

    setRecognitionError(null);
    setStatusMessage("Listening...");
    setStatusType("info");

    try {
      recognition.start();
      setRecognitionActive(true);
    } catch {
      setRecognitionError("Unable to access microphone. Please try again.");
      setStatusMessage("Unable to access microphone.");
      setStatusType("error");
      setRecognitionActive(false);
    }
  };

  const sendAnswerText = async (text, source = "text") => {
    const trimmed = text?.trim();
    if (!trimmed || loading || !selectedCategory) {
      return;
    }

    setInput("");
    setLoading(true);
    setLoadingPhase(source === "voice" ? "voice-answer" : "text-answer");
    setStatusMessage(
      source === "voice" ? "Sending your voice answer..." : "Submitting your answer..."
    );
    setStatusType("info");

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: trimmed,
        type: "answer",
        timestamp: new Date(),
      },
    ]);

    try {
      const res = await sendAnswer(trimmed, sessionId);

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: res.feedback,
          type: "feedback",
          analysis: res,
          timestamp: new Date(),
        },
      ]);

      setStatusMessage("Feedback ready. Next question coming up...");
      setStatusType("success");

      setTimeout(() => {
        loadQuestion();
      }, 2500);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: error.message || "Sorry, something went wrong while sending your answer.",
          type: "error",
          timestamp: new Date(),
        },
      ]);
      setStatusMessage("Unable to submit answer.");
      setStatusType("error");
    } finally {
      setLoading(false);
      setLoadingPhase("idle");
    }
  };

  const handleRetry = async () => {
    if (!selectedCategory) {
      await loadCategories();
      return;
    }

    setStatusMessage("Retrying...");
    setStatusType("info");
    await loadQuestion();
  };

  const handleBackToCategories = async () => {
    setSelectedCategory(null);
    setMessages([]);
    setSessionId(null);
    setInput("");
    setRecognitionError(null);
    setStatusMessage("Loading categories...");
    setStatusType("info");
    await loadCategories();
  };

  const handleSend = async () => {
    await sendAnswerText(input, "text");
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return "#22c55e";
    if (score >= 0.6) return "#f59e0b";
    if (score >= 0.4) return "#f97316";
    return "#ef4444";
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return "Excellent";
    if (score >= 0.6) return "Good";
    if (score >= 0.4) return "Fair";
    return "Needs Work";
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-mark">HM</span>
            <div>
              <h1>HireMentor</h1>
              <p className="subtitle">AI interview practice for sharper answers and calmer prep</p>
            </div>
          </div>
        </div>
      </div>

      {showLanding ? (
        <main className="landing-panel">
          <section className="hero-card">
            <div className="hero-copy">
              <span className="eyebrow">Interview Practice Platform</span>
              <h2>Start with the right track, then unlock the live question and answer workspace.</h2>
              <p>
                HireMentor helps you practice category-based interview rounds with instant feedback on
                quality, coverage, and clarity.
              </p>
            </div>

            <div className="hero-stats">
              <div className="stat-card">
                <span className="stat-value">{categories.length || "Any"}</span>
                <span className="stat-label">practice tracks</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">Voice</span>
                <span className="stat-label">answer support</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">Instant</span>
                <span className="stat-label">feedback loop</span>
              </div>
            </div>
          </section>

          <section className="highlights-grid">
            {LANDING_HIGHLIGHTS.map((item) => (
              <article key={item.title} className="highlight-card">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </section>

          <section className="category-panel">
            <div className="category-intro">
              <h3>Select a category</h3>
              <p>The chat workspace appears right after you choose a track.</p>
            </div>

            {categoryError && (
              <div className="status-banner status-error">
                <span>{categoryError}</span>
                <button className="retry-button" onClick={handleRetry} disabled={categoryLoading}>
                  Retry
                </button>
              </div>
            )}

            {categories.length > 0 ? (
              <div className="category-grid">
                {categories.map((category) => (
                  <button
                    key={category}
                    className="category-card"
                    onClick={() => handleCategorySelect(category)}
                    disabled={categoryLoading || loading}
                  >
                    <span className="category-name">{category}</span>
                    <span className="category-meta">Start practice</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="general-start-card">
                <p>Category data is not available right now, but you can still continue with a general round.</p>
                <button
                  className="general-start-button"
                  onClick={handleGeneralStart}
                  disabled={categoryLoading || loading}
                >
                  Start general interview
                </button>
              </div>
            )}

            {(categoryLoading || statusMessage) && (
              <div className={`status-banner status-${statusType}`}>
                <span>{categoryLoading ? "Loading categories..." : statusMessage}</span>
              </div>
            )}
          </section>
        </main>
      ) : (
        <>
          <div className="selected-category-banner">
            <span>
              Category: <strong>{selectedCategory}</strong>
            </span>
            <button className="change-category-button" onClick={handleBackToCategories} disabled={loading}>
              Change category
            </button>
          </div>

          <div className="chat-shell">
            <div className="chat-messages">
              {statusMessage && messages.length === 0 && (
                <div className={`status-banner status-${statusType}`}>
                  <span>{statusMessage}</span>
                  {statusType === "error" && (
                    <button className="retry-button" onClick={handleRetry} disabled={loading}>
                      Retry
                    </button>
                  )}
                </div>
              )}

              {messages.map((msg, index) => (
                <div key={`${msg.type}-${index}`} className={`message ${msg.sender}-message`}>
                  <div className="message-avatar">{msg.sender === "user" ? "You" : "AI"}</div>
                  <div className="message-content">
                    <div className="message-text">{msg.text}</div>

                    {msg.type === "feedback" && msg.analysis && (
                      <div className="analysis-panel">
                        <div className="analysis-header">
                          <h4>Performance analysis</h4>
                        </div>

                        <div className="score-grid">
                          <div className="score-item">
                            <div className="score-label">Overall Score</div>
                            <div
                              className="score-value"
                              style={{ color: getScoreColor(msg.analysis.final_score) }}
                            >
                              {Math.round(msg.analysis.final_score * 100)}%
                            </div>
                            <div className="score-desc">{getScoreLabel(msg.analysis.final_score)}</div>
                          </div>

                          <div className="score-item">
                            <div className="score-label">Keyword Match</div>
                            <div
                              className="score-value"
                              style={{ color: getScoreColor(msg.analysis.keyword_score) }}
                            >
                              {Math.round(msg.analysis.keyword_score * 100)}%
                            </div>
                          </div>

                          <div className="score-item">
                            <div className="score-label">Semantic Understanding</div>
                            <div
                              className="score-value"
                              style={{ color: getScoreColor(msg.analysis.semantic_score) }}
                            >
                              {Math.round(msg.analysis.semantic_score * 100)}%
                            </div>
                          </div>
                        </div>

                        {msg.analysis.matched?.length > 0 && (
                          <div className="keywords-section">
                            <span className="keywords-label">Keywords Found</span>
                            <div className="keywords-list">
                              {msg.analysis.matched.map((keyword, idx) => (
                                <span key={idx} className="keyword-tag matched">
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.analysis.missing?.length > 0 && (
                          <div className="keywords-section">
                            <span className="keywords-label">Consider Including</span>
                            <div className="keywords-list">
                              {msg.analysis.missing.slice(0, 3).map((keyword, idx) => (
                                <span key={idx} className="keyword-tag missing">
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="message-time">
                      {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                </div>
              ))}

              {(isSendingAnswer || isLoadingQuestion) && (
                <div className="message bot-message">
                  <div className="message-avatar">AI</div>
                  <div className="message-content">
                    <div className="message-text loader-card">
                      <div className="typing-indicator" aria-hidden="true">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <div className="loader-copy">
                        {isVoiceSubmitting
                          ? "Sending your voice answer and preparing feedback..."
                          : isSendingAnswer
                            ? "Reviewing your answer..."
                            : "Preparing the next question..."}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        </>
      )}

      {showChatInput && (
        <div className="chat-input">
          <div className="input-container">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your answer here..."
              disabled={loading}
              rows="1"
              className="message-input"
            />
            <button
              onClick={handleMicClick}
              disabled={loading || !speechSupported}
              className={`mic-button ${recognitionActive ? "active" : ""}`}
              type="button"
              aria-label={recognitionActive ? "Stop listening" : "Start voice input"}
            >
              {recognitionActive ? "Stop" : "Voice"}
            </button>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="send-button"
            >
              {isSendingAnswer ? "Sending" : "Send"}
            </button>
          </div>

          <div className="input-footer">
            <span className="hint">Answer clearly, mention key concepts, and explain your reasoning.</span>
            {recognitionActive && <span className="listening-indicator">Listening for your answer...</span>}
            {isVoiceSubmitting && <span className="voice-status">Voice answer is being sent for review...</span>}
            {recognitionError && <span className="speech-error">{recognitionError}</span>}
            {!speechSupported && (
              <span className="speech-error">Speech recognition is not supported in this browser.</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;

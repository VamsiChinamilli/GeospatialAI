
// src/components/ChatPanel.jsx

import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send } from 'lucide-react';

export default function ChatPanel({
  conversation = [],
  isStreaming,
  onSendMessage,
}) {
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation, isStreaming]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!input.trim() || isStreaming) return;

    onSendMessage(input);
    setInput('');
  };

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f7f5ed',
        backgroundImage:
          'radial-gradient(#e2dfd2 1px, transparent 1px)',
        backgroundSize: '20px 20px',
        color: '#1c1917',
        padding: '24px',
        boxSizing: 'border-box',
        minHeight: 0,
        overflow: 'hidden',
        fontFamily:
          '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      {/* Header */}
      <div
        style={{
          marginBottom: '18px',
          paddingBottom: '16px',
          borderBottom: '1px solid #e5e7eb',
        }}
      >
        <div
          style={{
            fontSize: '10px',
            fontFamily: 'monospace',
            letterSpacing: '0.08em',
            color: '#6b7280',
            marginBottom: '6px',
          }}
        >
          COPILOT INTELLIGENCE CHANNEL
        </div>

        <h3
          style={{
            margin: 0,
            fontSize: '22px',
            fontWeight: '700',
            fontFamily:
              '"Playfair Display", Georgia, serif',
            color: '#1c1917',
          }}
        >
          Summary of Analysis
        </h3>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          paddingRight: '4px',
          minHeight: 0,
        }}
      >
        {conversation.length === 0 && !isStreaming ? (
          <div
            style={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              color: '#6b7280',
              fontSize: '13px',
              lineHeight: '1.7',
            }}
          >
            Select a spatial footprint to initialize the Urban Heat
            Island Copilot briefing stream.
          </div>
        ) : (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              paddingBottom: '16px',
            }}
          >
            {conversation.map((msg, i) => {
              const isUser = msg.role === 'user';

              return (
                <div
                  key={i}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '16px',
                    padding: '18px 20px',
                    boxShadow:
                      '0 2px 10px rgba(0,0,0,0.03)',
                    alignSelf: isUser ? 'flex-end' : 'stretch',
                    maxWidth: isUser ? '92%' : '100%',
                  }}
                >
                  <div
                    style={{
                      fontSize: '10px',
                      fontFamily: 'monospace',
                      letterSpacing: '0.08em',
                      color: '#6b7280',
                      marginBottom: '8px',
                    }}
                  >
                    {isUser ? 'FIELD OPERATOR QUERY' : 'COPILOT ANALYSIS'}
                  </div>

                  <div
                    style={{
                      color: '#374151',
                      fontSize: '13.5px',
                      lineHeight: '1.7',
                    }}
                  >
                    <ReactMarkdown
                      components={{
                        h1: (props) => (
                          <h1
                            style={{
                              fontSize: '18px',
                              fontWeight: '700',
                              margin: '0 0 12px 0',
                              color: '#111827',
                              fontFamily:
                                '"Playfair Display", Georgia, serif',
                            }}
                            {...props}
                          />
                        ),

                        h2: (props) => (
                          <h2
                            style={{
                              fontSize: '15px',
                              fontWeight: '700',
                              margin: '14px 0 8px 0',
                              color: '#111827',
                            }}
                            {...props}
                          />
                        ),

                        p: (props) => (
                          <p
                            style={{
                              margin: '0 0 10px 0',
                              color: '#374151',
                            }}
                            {...props}
                          />
                        ),

                        ul: (props) => (
                          <ul
                            style={{
                              paddingLeft: '18px',
                              margin: '6px 0 10px 0',
                            }}
                            {...props}
                          />
                        ),

                        li: (props) => (
                          <li
                            style={{
                              marginBottom: '4px',
                            }}
                            {...props}
                          />
                        ),

                        strong: (props) => (
                          <strong
                            style={{
                              color: '#111827',
                              fontWeight: '600',
                            }}
                            {...props}
                          />
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              );
            })}

            {isStreaming && (
              <div
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '16px',
                  padding: '16px 20px',
                  boxShadow:
                    '0 2px 10px rgba(0,0,0,0.03)',
                  color: '#2d5a27',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  letterSpacing: '0.04em',
                }}
              >
                Generating Copilot environmental briefing…
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        style={{
          marginTop: '16px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '14px',
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Copilot regarding thermal anomalies or risk patterns…"
          disabled={isStreaming}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            backgroundColor: 'transparent',
            fontSize: '13.5px',
            color: '#1c1917',
            fontFamily: 'inherit',
          }}
        />

        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '10px',
            border: '1px solid #d1d5db',
            backgroundColor:
              isStreaming || !input.trim()
                ? '#f3f4f6'
                : '#2d5a27',
            color:
              isStreaming || !input.trim()
                ? '#9ca3af'
                : '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor:
              isStreaming || !input.trim()
                ? 'not-allowed'
                : 'pointer',
            transition: 'all 0.2s ease',
          }}
        >
          <Send style={{ width: '16px', height: '16px' }} />
        </button>
      </form>
    </div>
  );
}


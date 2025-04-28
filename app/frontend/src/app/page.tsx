'use client';
import { useState, useRef, useEffect } from 'react';
import styles from './page.module.css';

interface Message {
  id: number;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  error?: boolean;
}

interface BackendMessage {
  content: string;
  role: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messageListRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleScroll = () => {
      if (messageListRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = messageListRef.current;
        const isBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShowScrollButton(!isBottom);
      }
    };

    messageListRef.current?.addEventListener('scroll', handleScroll);
    return () => messageListRef.current?.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      id: Date.now(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const messageHistory: BackendMessage[] = messages.map(msg => ({
        content: msg.content,
        role: msg.role
      }));

      messageHistory.push({
        content: inputMessage,
        role: 'user'
      });

      const response = await fetch('/agno_ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: messageHistory }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const assistantMessage: Message = {
        id: Date.now(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        content: 'Sorry, there was an error processing your request.',
        role: 'assistant',
        timestamp: new Date(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async (messageIndex: number) => {
    if (messageIndex < 0 || !messages[messageIndex]) return;

    const messagesUpToRetry = messages.slice(0, messageIndex + 1);
    setMessages(messagesUpToRetry);
    setIsLoading(true);

    try {
      const messageHistory: BackendMessage[] = messagesUpToRetry.map(msg => ({
        content: msg.content,
        role: msg.role
      }));

      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: messageHistory }),
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const assistantMessage: Message = {
        id: Date.now(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        content: 'Sorry, there was an error processing your request.',
        role: 'assistant',
        timestamp: new Date(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h1>AgenticRAG Assistant</h1>
        <p className={styles.subtitle}>Ask me anything about your documents</p>
      </div>
      
      <div className={styles.messageList} ref={messageListRef}>
        {messages.length === 0 && (
          <div className={styles.welcomeMessage}>
            👋 Hi! I'm here to help you with your documents. What would you like to know?
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`${styles.message} ${
              message.role === 'user' ? styles.userMessage : styles.assistantMessage
            } ${message.error ? styles.errorMessage : ''} ${styles.fadeIn}`}
          >
            <div className={styles.messageContent}>
              {message.content}
            </div>
            <div className={styles.messageFooter}>
              <span className={styles.messageTimestamp}>
                {message.timestamp.toLocaleTimeString()}
              </span>
              {message.error && (
                <button 
                  className={styles.retryButton}
                  onClick={() => handleRetry(index - 1)}
                  disabled={isLoading}
                >
                  ↻ Retry
                </button>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className={`${styles.loadingIndicator} ${styles.fadeIn}`}>
            <div className={styles.typingDots}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      {showScrollButton && (
        <button 
          className={styles.scrollToBottomButton} 
          onClick={scrollToBottom}
        >
          ↓
        </button>
      )}

      <form onSubmit={handleSendMessage} className={styles.inputForm}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          className={styles.messageInput}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className={styles.sendButton} 
          disabled={isLoading || !inputMessage.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { 
  FiSend, FiUser, FiServer, FiClock, FiAlertCircle, 
  FiCheckCircle, FiHardDrive, FiInfo, FiChevronDown 
} from 'react-icons/fi';
import { 
  BsQuestionCircle, BsShieldCheck, BsPeople, 
  BsExclamationTriangle, BsLightning 
} from 'react-icons/bs';
import { RiCloseCircleLine, RiDatabase2Line } from 'react-icons/ri';
import { IoMdArrowDropdown } from 'react-icons/io';
import { AiOutlineCloudServer } from 'react-icons/ai';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedIncidents, setExpandedIncidents] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleIncidentExpand = (incidentNumber) => {
    setExpandedIncidents(prev => ({
      ...prev,
      [incidentNumber]: !prev[incidentNumber]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = { 
      text: inputValue, 
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:7000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue
        }),
        mode: 'cors'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Network response was not ok');
      }

      const data = await response.json();
      if (!data.formatted_response) {
        throw new Error('Invalid response format from server');
      }

      const botMessage = { 
        text: data.formatted_response, 
        sender: 'bot', 
        rawData: data.raw_data,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError(err.message || 'Failed to get response. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderIncidentDetails = (rawData) => {
    if (!rawData || !rawData.results || !rawData.results[0] || !rawData.results[0].incident_details) {
      return null;
    }

    const incident = rawData.results[0].incident_details;
    const isExpanded = expandedIncidents[incident.number];
    
    const priorityColor = incident.priority?.includes('High') ? 'text-red-500' : 
                         incident.priority?.includes('Medium') ? 'text-yellow-500' : 'text-green-500';
    
    const priorityIcon = incident.priority?.includes('High') ? 
                         <BsExclamationTriangle className="mr-1" /> :
                         incident.priority?.includes('Medium') ? 
                         <BsLightning className="mr-1" /> : 
                         <BsShieldCheck className="mr-1" />;

    return (
      <div className="incident-card mt-4 p-4 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
        <div 
          className="incident-header flex justify-between items-center cursor-pointer"
          onClick={() => toggleIncidentExpand(incident.number)}
        >
          <div className="flex items-center">
            <div className={`priority-indicator ${priorityColor} mr-3`}>
              {priorityIcon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">{incident.number}</h3>
              <p className="text-sm text-gray-500">{incident.description?.split('-')[0]}</p>
            </div>
          </div>
          <div className="flex items-center">
            <span className={`status-pill ${incident.state === 'Closed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'} px-2 py-1 rounded-full text-xs mr-3`}>
              {incident.state}
            </span>
            <FiChevronDown className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
          </div>
        </div>
        
        {isExpanded && (
          <div className="incident-details mt-4 pt-4 border-t border-gray-100">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <FiHardDrive className="mr-2" /> Incident Number:
                </span>
                <span className="detail-value font-medium text-gray-800">{incident.number}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <BsShieldCheck className="mr-2" /> State:
                </span>
                <span className="detail-value">
                  {incident.state === 'Closed' ? (
                    <span className="flex items-center text-green-600">
                      <FiCheckCircle className="mr-1" /> Closed
                    </span>
                  ) : (
                    <span className="flex items-center text-yellow-600">
                      <FiAlertCircle className="mr-1" /> {incident.state}
                    </span>
                  )}
                </span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <FiAlertCircle className="mr-2" /> Priority:
                </span>
                <span className={`detail-value font-medium ${priorityColor} flex items-center`}>
                  {priorityIcon} {incident.priority}
                </span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <FiUser className="mr-2" /> Opened By:
                </span>
                <span className="detail-value text-gray-800">{incident.opened_by?.display_value}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <FiUser className="mr-2" /> Assigned To:
                </span>
                <span className="detail-value text-gray-800">{incident.assigned_to?.display_value}</span>
              </div>
              
              <div className="detail-item">
                <span className="detail-label flex items-center text-gray-500 text-sm">
                  <BsPeople className="mr-2" /> Assignment Group:
                </span>
                <span className="detail-value text-gray-800">{incident.assignment_group?.display_value}</span>
              </div>
            </div>
            
            {incident.description && (
              <div className="mt-4">
                <h4 className="text-md font-medium mb-2 flex items-center text-gray-700">
                  <BsQuestionCircle className="mr-2" /> Description
                </h4>
                <p className="text-gray-700 bg-gray-50 p-3 rounded border border-gray-200 text-sm">
                  {incident.description}
                </p>
              </div>
            )}
            
            <div className="mt-4 flex justify-between items-center text-xs text-gray-400">
              <div className="flex items-center">
                <AiOutlineCloudServer className="mr-1" />
                <span>AWS CloudWatch</span>
              </div>
              <div className="flex items-center">
                <FiClock className="mr-1" />
                <span>Last updated: {new Date().toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="app-container bg-gray-50">
      <header className="app-header bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="header-content max-w-6xl mx-auto px-4">
          <div className="logo-container flex items-center">
            <div className="logo-icon-container bg-white/20 p-2 rounded-lg mr-3">
              <RiDatabase2Line className="logo-icon text-white text-2xl" />
            </div>
            <div>
              <h1 className="text-white text-2xl font-bold">Incident Query System</h1>
              <p className="tagline text-white/90 text-sm">AI-powered incident management assistant</p>
            </div>
          </div>
        </div>
      </header>

      <main className="chat-container flex-1 max-w-6xl mx-auto px-4 py-6">
        <div className="messages-container bg-white rounded-xl shadow-sm border border-gray-200">
          {messages.length === 0 ? (
            <div className="welcome-message p-8 text-center">
              <div className="welcome-icon mx-auto mb-4 bg-indigo-100 text-indigo-600 p-4 rounded-full w-16 h-16 flex items-center justify-center">
                <FiServer className="text-2xl" />
              </div>
              <h2 className="welcome-title text-2xl font-bold text-gray-800 mb-3">Welcome to Incident Query Assistant</h2>
              <p className="welcome-text text-gray-600 mb-6">
                Ask me anything about incidents in our system. I can help you find details, status, and resolution information.
              </p>
              <div className="example-questions bg-gray-50 p-4 rounded-lg max-w-2xl mx-auto text-left">
                <h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center">
                  <FiInfo className="mr-2" /> TRY ASKING:
                </h3>
                <ul className="space-y-2">
                  <li className="text-sm text-gray-700 bg-white p-2 rounded border border-gray-200 hover:bg-gray-100 cursor-pointer" onClick={() => setInputValue("Give me details of incident INC8740564")}>
                    "Give me details of incident INC8740564"
                  </li>
                  <li className="text-sm text-gray-700 bg-white p-2 rounded border border-gray-200 hover:bg-gray-100 cursor-pointer" onClick={() => setInputValue("Show me all high priority incidents")}>
                    "Show me all high priority incidents"
                  </li>
                  <li className="text-sm text-gray-700 bg-white p-2 rounded border border-gray-200 hover:bg-gray-100 cursor-pointer" onClick={() => setInputValue("What's the status of recent disk issues?")}>
                    "What's the status of recent disk issues?"
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="messages-content p-4">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.sender} mb-6`}>
                  <div className="message-sender">
                    {message.sender === 'user' ? (
                      <div className="user-avatar bg-indigo-100 text-indigo-600 p-2 rounded-full">
                        <FiUser className="text-lg" />
                      </div>
                    ) : (
                      <div className="bot-avatar bg-purple-100 text-purple-600 p-2 rounded-full">
                        <FiServer className="text-lg" />
                      </div>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header flex items-center mb-1">
                      <span className="font-medium text-gray-700">
                        {message.sender === 'user' ? 'You' : 'Incident Assistant'}
                      </span>
                      <span className="text-xs text-gray-400 ml-2">{message.timestamp}</span>
                    </div>
                    <div className={`message-text ${message.sender === 'user' ? 'bg-indigo-50 text-gray-800' : 'bg-white text-gray-800'} p-3 rounded-lg`}>
                      {message.text}
                    </div>
                    {message.sender === 'bot' && message.rawData && renderIncidentDetails(message.rawData)}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message bot flex mb-6">
                  <div className="message-sender">
                    <div className="bot-avatar bg-purple-100 text-purple-600 p-2 rounded-full">
                      <FiServer className="text-lg" />
                    </div>
                  </div>
                  <div className="message-content">
                    <div className="message-header flex items-center mb-1">
                      <span className="font-medium text-gray-700">Incident Assistant</span>
                      <span className="text-xs text-gray-400 ml-2">{new Date().toLocaleTimeString()}</span>
                    </div>
                    <div className="message-text bg-white p-3 rounded-lg">
                      <div className="loading-dots flex space-x-1">
                        <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        <div className="dot w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {error && (
          <div className="error-message bg-red-50 text-red-600 p-3 rounded-lg flex items-center mt-4">
            <RiCloseCircleLine className="mr-2" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="input-container mt-4 bg-white p-1 rounded-xl shadow-sm border border-gray-200 flex">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about an incident (e.g. 'Show INC8740564 details')..."
            className="chat-input flex-1 border-none focus:ring-0 bg-transparent"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className={`send-button flex items-center justify-center w-10 h-10 rounded-lg ${inputValue.trim() ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-300 cursor-not-allowed'}`}
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? (
              <div className="loading-spinner w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <FiSend className="text-white" />
            )}
          </button>
        </form>
      </main>

      <footer className="app-footer bg-white border-t border-gray-200 py-3">
        <div className="max-w-6xl mx-auto px-4 text-center text-xs text-gray-500">
          <p>Incident Query Assistant • {new Date().getFullYear()} • Powered by AI</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
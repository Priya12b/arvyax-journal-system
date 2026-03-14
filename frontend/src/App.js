import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [userId, setUserId] = useState('123');
  const [ambience, setAmbience] = useState('forest');
  const [text, setText] = useState('');
  const [entries, setEntries] = useState([]);
  const [insights, setInsights] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null); 
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  const notify = (message) => {
    setStatus(message);
    setTimeout(() => setStatus(''), 3000);
  };

  const createEntry = async () => {
    if (!text.trim()) {
      notify('Please write something first!');
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/journal`, { userId, ambience, text });
      setText('');
      notify('Entry saved successfully!');
      loadEntries();
    } catch (err) {
      notify('Error saving entry');
    } finally {
      setLoading(false);
    }
  };

  const loadEntries = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/journal/${userId}`);
      setEntries(res.data);
    } catch (err) {
      notify('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const analyzeEntry = async (entryId, entryText) => {
    setLoading(true);
    setAnalysisResult(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/api/journal/analyze`, {
        entryId,
        text: entryText,
      });
      setAnalysisResult(res.data);
      notify('Analysis complete!');
    } catch (err) {
      notify('AI Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const loadInsights = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/api/journal/insights/${userId}`);
      setInsights(res.data);
    } catch (err) {
      notify('Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App" style={{ maxWidth: '600px', margin: 'auto', padding: '20px', fontFamily: 'Arial' }}>
      <h1>ArvyaX Journal System</h1>
      
      {status && <div style={{ background: '#333', color: '#fff', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}>{status}</div>}

      <div className="input-section" style={{ marginBottom: '30px', border: '1px solid #ddd', padding: '15px' }}>
        <h3>New Entry</h3>
        <input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID" style={{ width: '100%', marginBottom: '10px' }} />
        <select value={ambience} onChange={e => setAmbience(e.target.value)} style={{ width: '100%', marginBottom: '10px' }}>
          <option>forest</option>
          <option>ocean</option>
          <option>mountain</option>
        </select>
        <textarea 
          value={text} 
          onChange={e => setText(e.target.value)} 
          placeholder="How was your nature session?" 
          style={{ width: '100%', height: '80px', marginBottom: '10px' }} 
        />
        <button onClick={createEntry} disabled={loading}>{loading ? 'Processing...' : 'Save Entry'}</button>
      </div>

      {analysisResult && (
        <div style={{ background: '#e1f5fe', padding: '15px', borderRadius: '8px', marginBottom: '20px', color: '#0b1220' }}>
          <h4>AI Emotion Analysis:</h4>
          <p><strong>Emotion:</strong> {analysisResult.emotion}</p>
          <p><strong>Summary:</strong> {analysisResult.summary}</p>
          <p><strong>Keywords:</strong> {analysisResult.keywords?.join(', ')}</p>
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={loadEntries}>View History</button>
        <button onClick={loadInsights}>View Insights</button>
      </div>

      {insights && (
        <div style={{ background: '#f9f9f9', color: '#0b1220', padding: '15px', marginBottom: '20px', borderLeft: '5px solid #4caf50' }}>
          <strong>Statistics:</strong> Entries: {insights.totalEntries} | Top Mood: {insights.topEmotion}
        </div>
      )}

      <div className="history">
        <h3>Previous Entries</h3>
        {entries.length === 0 && <p>No entries found for this user.</p>}
        {entries.map((entry, index) => (
          <div key={index} style={{ borderBottom: '1px solid #eee', padding: '10px 0', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <strong>{entry.ambience}:</strong> {entry.text}
            </div>
            <button onClick={() => analyzeEntry(entry.id, entry.text)}>Analyze AI</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
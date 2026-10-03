import React, { useState, useEffect } from 'react';
import { analysisApi, qaApi, AnswerResponse, Clause, ReviewFlag } from '@/services/api';
import './DashboardPage.css';

interface DashboardPageProps {
  documentId: string;
  onBack: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ documentId, onBack }) => {
  const [activeTab, setActiveTab] = useState<'clauses' | 'flags' | 'qa'>('clauses');
  const [clauses, setClauses] = useState<Clause[]>([]);
  const [flags, setFlags] = useState<ReviewFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [answering, setAnswering] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Analyze document
        await analysisApi.analyzeDocument(documentId);

        // Load clauses and flags
        const [clausesData, flagsData] = await Promise.all([
          analysisApi.getClauses(documentId),
          analysisApi.getFlags(documentId),
        ]);

        setClauses(clausesData);
        setFlags(flagsData.flags || []);
      } catch (error) {
        console.error('Failed to load document data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [documentId]);

  const handleAskQuestion = async () => {
    if (!question.trim()) return;

    setAnswering(true);
    try {
      const result = await qaApi.askQuestion(documentId, question);
      setAnswer(result);
    } catch (error) {
      console.error('Failed to answer question:', error);
    } finally {
      setAnswering(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return '#d32f2f';
      case 'medium':
        return '#f57c00';
      case 'low':
        return '#fbc02d';
      default:
        return '#999';
    }
  };

  if (loading) {
    return <div className="dashboard-page"><p>Loading...</p></div>;
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <button className="back-button" onClick={onBack}>← Back</button>
        <h1>Document Analysis</h1>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'clauses' ? 'active' : ''}`}
          onClick={() => setActiveTab('clauses')}
        >
          Clauses ({clauses.length})
        </button>
        <button
          className={`tab ${activeTab === 'flags' ? 'active' : ''}`}
          onClick={() => setActiveTab('flags')}
        >
          Risk Flags ({flags.length})
        </button>
        <button
          className={`tab ${activeTab === 'qa' ? 'active' : ''}`}
          onClick={() => setActiveTab('qa')}
        >
          Ask Question
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'clauses' && (
          <div className="clauses-view">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Reasoning</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {clauses.map((clause) => (
                  <tr key={clause.id}>
                    <td>{clause.clause_type}</td>
                    <td>{clause.reasoning}</td>
                    <td>{clause.confidence ? (clause.confidence * 100).toFixed(0) + '%' : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'flags' && (
          <div className="flags-view">
            {flags.map((flag, idx) => (
              <div
                key={idx}
                className="flag-card"
                style={{ borderLeft: `4px solid ${getSeverityColor(flag.severity)}` }}
              >
                <div className="flag-header">
                  <h3>{flag.category}</h3>
                  <span className="severity" style={{ color: getSeverityColor(flag.severity) }}>
                    {flag.severity.toUpperCase()}
                  </span>
                </div>
                <p className="flag-reason">{flag.reason}</p>
                <div className="flag-source">
                  <small>Page {flag.source_page}</small>
                  {flag.source_clause && <small> • Clause {flag.source_clause}</small>}
                  {flag.is_rule_based && <small> • Rule-based</small>}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'qa' && (
          <div className="qa-view">
            <div className="question-input">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                placeholder="Ask a question about the document..."
              />
              <button onClick={handleAskQuestion} disabled={answering}>
                {answering ? 'Answering...' : 'Ask'}
              </button>
            </div>

            {answer && (
              <div className="answer-section">
                <div className={`evidence ${answer.has_sufficient_evidence ? 'sufficient' : 'insufficient'}`}>
                  Evidence Score: {(answer.evidence_score * 100).toFixed(0)}% -
                  {answer.has_sufficient_evidence ? ' ✓ Sufficient' : ' ⚠ Insufficient'}
                </div>
                <div className="answer-text">
                  <p>{answer.answer}</p>
                </div>
                {answer.citations.length > 0 && (
                  <div className="citations">
                    <h4>Citations:</h4>
                    {answer.citations.map((citation, idx) => (
                      <div key={idx} className="citation">
                        <small>
                          Page {citation.page_number}
                          {citation.section_name && ` • ${citation.section_name}`}
                          {citation.clause_id && ` • Clause ${citation.clause_id}`}
                        </small>
                        <p>{citation.text}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

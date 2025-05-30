import { useState } from 'react';
import { useAddWordComponentApiWordsWordIdComponentsPost } from './api/components/components';
import { useReadWordsApiWordsGet } from './api/words/words';

const COMPONENT_TYPES = ['prefix', 'root', 'suffix', 'infix', 'postfix', 'other'];

export default function WordComponentForm() {
  const { data: wordsData, isLoading: wordsLoading, error: wordsError } = useReadWordsApiWordsGet();
  const [wordId, setWordId] = useState<number | ''>('');
  const [type, setType] = useState('root');
  const [text, setText] = useState('');
  const [meanings, setMeanings] = useState<string[]>([]);
  const [newMeaning, setNewMeaning] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [order, setOrder] = useState(0);
  const addComponent = useAddWordComponentApiWordsWordIdComponentsPost();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    if (!wordId) {
      setStatus('Please select a word');
      return;
    }
    addComponent.mutate(
      { wordId: Number(wordId), data: { type, text, meanings, order } },
      {
        onSuccess: () => {
          setStatus('Component created!');
          setType('root');
          setText('');
          setMeanings([]);
          setNewMeaning('');
          setWordId('');
          setOrder(0);
        },
        onError: (err: any) => {
          setStatus('Error: ' + (err?.message || 'Unknown error'));
        },
      }
    );
  };

  return (
    <div style={{ maxWidth: 500, margin: '0 auto' }}>
      <h2>Add Word Component</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label><strong>Word:</strong></label><br />
          {wordsLoading ? (
            <span>Loading words...</span>
          ) : wordsError ? (
            <span style={{ color: 'red' }}>Error loading words</span>
          ) : (
            <select value={wordId} onChange={e => setWordId(e.target.value ? Number(e.target.value) : '')} required>
              <option value="">Select a word</option>
              {wordsData?.data?.map((w: any) => (
                <option key={w.id} value={w.id}>{w.text}</option>
              ))}
            </select>
          )}
        </div>
        <div style={{ marginBottom: 12 }}>
          <label><strong>Type:</strong></label><br />
          <select value={type} onChange={e => setType(e.target.value)} required>
            {COMPONENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label><strong>Text:</strong></label><br />
          <input value={text} onChange={e => setText(e.target.value)} required style={{ width: 200 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <label><strong>Meanings:</strong></label><br />
          <ul>
            {meanings.map((m, idx) => (
              <li key={idx}>
                {m} <button type="button" onClick={() => setMeanings(meanings.filter((_, i) => i !== idx))}>Delete</button>
              </li>
            ))}
          </ul>
          <input value={newMeaning} onChange={e => setNewMeaning(e.target.value)} placeholder="New meaning" style={{ width: 200 }} />
          <button type="button" onClick={() => { if (newMeaning.trim()) { setMeanings([...meanings, newMeaning]); setNewMeaning(''); } }}>Add</button>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label><strong>Order:</strong></label><br />
          <input type="number" value={order} onChange={e => setOrder(Number(e.target.value))} style={{ width: 100 }} />
        </div>
        <button type="submit" disabled={addComponent.isPending}>Create Component</button>
        {status && <div style={{ marginTop: 8 }}>{status}</div>}
      </form>
    </div>
  );
} 
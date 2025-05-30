import { useState } from 'react';
import { useReadWordsApiWordsGet } from '../api/words/words';
import { useCreatePhraseApiPhrasesPost } from '../api/phrases/phrases';
import WordChip from './WordChip';
import type { WordResponse } from '../api/model';
import Select from 'react-select';

export default function PhraseBuilder() {
    const { data, isLoading, error } = useReadWordsApiWordsGet();
    const [selected, setSelected] = useState<WordResponse[]>([]);
    const [status, setStatus] = useState<string | null>(null);
    const createPhraseMutation = useCreatePhraseApiPhrasesPost();
    const [selectValue, setSelectValue] = useState<any>(null);

    if (isLoading) return <div>Loading words...</div>;
    if (error) return <div>Error loading words: {error.message}</div>;
    if (!data?.data?.length) return <div>No words available.</div>;

    const availableWords = data.data.filter(
        word => !selected.some(selectedWord => selectedWord.id === word.id)
    );

    const options = availableWords.map(word => ({ value: word.id, label: word.text, word }));

    return (
        <div>
            <h3>Phrase Builder</h3>
            <div style={{ marginBottom: 12, maxWidth: 400 }}>
                <Select
                    options={options}
                    value={selectValue}
                    onChange={option => {
                        if (option && option.word) {
                            setSelected([...selected, option.word]);
                            setSelectValue(null);
                        }
                    }}
                    placeholder="Type to search and add a word..."
                    isClearable
                    isSearchable
                />
            </div>
            <div style={{ marginBottom: 12 }}>
                <strong>Selected: </strong>
                {selected.length === 0 && <span>none</span>}
                {selected.map((word, wordIndex) => (
                    <WordChip
                        key={word.id}
                        word={word.text}
                        onClick={() => setSelected(selected.filter((_, i) => i !== wordIndex))}
                    />
                ))}
            </div>
            <button
                disabled={selected.length === 0 || createPhraseMutation.isPending}
                onClick={() => {
                    setStatus(null);
                    createPhraseMutation.mutate(
                        { data: { words: selected.map(w => w.id) } },
                        {
                            onSuccess: () => {
                                setStatus('Phrase created!');
                                setSelected([]);
                            },
                            onError: (err: any) => {
                                setStatus('Error: ' + (err?.message || 'Unknown error'));
                            },
                        }
                    );
                }}
            >
                Create Phrase
            </button>
            {status && <div style={{ marginTop: 8 }}>{status}</div>}
        </div>
    );
}

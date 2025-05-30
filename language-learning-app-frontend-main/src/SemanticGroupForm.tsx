import { useState } from 'react';
import { LEVELS } from './constants';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import { useReadWordsApiWordsGet } from './api/words/words';
import { useReadPhrasesApiPhrasesGet } from './api/phrases/phrases';
import Select from 'react-select';
import type { MultiValue } from 'react-select';

interface SemanticGroupFormProps {
    initial?: {
        name?: string;
        level?: string;
        frequency?: string;
        categories?: number[];
        word_ids?: number[];
        phrase_ids?: number[];
        explanation?: string;
        difference_explanation?: string;
    };
    onSubmit: (data: { name: string; level: string; frequency: string; categories: number[]; word_ids?: number[]; phrase_ids?: number[]; explanation?: string; difference_explanation?: string }) => void;
    submitLabel?: string;
}

export default function SemanticGroupForm({ initial, onSubmit, submitLabel = 'Save' }: SemanticGroupFormProps) {
    const [name, setName] = useState(initial?.name || '');
    const [level, setLevel] = useState(initial?.level || '');
    const [frequency, setFrequency] = useState(initial?.frequency || '');
    const [categories, setCategories] = useState<number[]>(initial?.categories || []);
    const [wordIds, setWordIds] = useState<number[]>(initial?.word_ids || []);
    const [phraseIds, setPhraseIds] = useState<number[]>(initial?.phrase_ids || []);
    const [explanation, setExplanation] = useState(initial?.explanation || '');
    const [differenceExplanation, setDifferenceExplanation] = useState(initial?.difference_explanation || '');
    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();
    const { data: wordsData, isLoading: wordsLoading } = useReadWordsApiWordsGet();
    const { data: phrasesData, isLoading: phrasesLoading } = useReadPhrasesApiPhrasesGet();

    return (
        <form
            onSubmit={e => {
                e.preventDefault();
                onSubmit({ name, level, frequency, categories, word_ids: wordIds, phrase_ids: phraseIds, explanation, difference_explanation: differenceExplanation });
            }}
            style={{ margin: 16 }}
        >
            <div style={{ marginBottom: 8 }}>
                <label><strong>Name:</strong></label><br />
                <input value={name} onChange={e => setName(e.target.value)} required style={{ width: 300 }} />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Level:</strong></label><br />
                <select value={level} onChange={e => setLevel(e.target.value)} style={{ width: 120 }}>
                    <option value="">—</option>
                    {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                </select>
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Frequency:</strong></label><br />
                <input value={frequency} onChange={e => setFrequency(e.target.value)} style={{ width: 120 }} />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Categories:</strong></label><br />
                <Select
                    isMulti
                    options={categoriesData?.data?.map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                    value={categoriesData?.data?.filter((cat: any) => categories.includes(cat.id)).map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                    onChange={(selected: MultiValue<{ value: number; label: string }>) => setCategories(selected.map(opt => opt.value))}
                />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Words:</strong></label><br />
                <Select
                    isMulti
                    isLoading={wordsLoading}
                    options={wordsData?.data?.map((w: any) => ({ value: w.id, label: w.text })) || []}
                    value={wordsData?.data?.filter((w: any) => wordIds.includes(w.id)).map((w: any) => ({ value: w.id, label: w.text })) || []}
                    onChange={(selected: MultiValue<{ value: number; label: string }>) => setWordIds(selected.map(opt => opt.value))}
                    placeholder="Add words to group..."
                />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Phrases:</strong></label><br />
                <Select
                    isMulti
                    isLoading={phrasesLoading}
                    options={phrasesData?.data?.map((p: any) => ({ value: p.id, label: p.words.map((w: any) => w.text).join(' ') })) || []}
                    value={phrasesData?.data?.filter((p: any) => phraseIds.includes(p.id)).map((p: any) => ({ value: p.id, label: p.words.map((w: any) => w.text).join(' ') })) || []}
                    onChange={(selected: MultiValue<{ value: number; label: string }>) => setPhraseIds(selected.map(opt => opt.value))}
                    placeholder="Add phrases to group..."
                />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Explanation:</strong></label><br />
                <textarea
                    value={explanation}
                    onChange={e => setExplanation(e.target.value)}
                    rows={3}
                    style={{ width: '100%' }}
                />
            </div>
            <div style={{ marginBottom: 8 }}>
                <label><strong>Difference explanation:</strong></label><br />
                <textarea
                    value={differenceExplanation}
                    onChange={e => setDifferenceExplanation(e.target.value)}
                    rows={3}
                    style={{ width: '100%' }}
                />
            </div>
            <button type="submit">{submitLabel}</button>
        </form>
    );
} 
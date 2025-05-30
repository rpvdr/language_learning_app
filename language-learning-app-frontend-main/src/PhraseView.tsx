import { useLocation, useNavigate } from 'react-router-dom';
import { useReadPhraseApiPhrasesPhraseIdGet, useDeletePhraseApiPhrasesPhraseIdDelete, useAddPhraseMeaningApiPhrasesPhraseIdMeaningsPost, useAddPhraseExampleApiPhrasesPhraseIdExamplesPost, useUpdatePhraseApiPhrasesPhraseIdPut } from './api/phrases/phrases';
import IsAdmin from './IsAdmin';
import { useState, useEffect, useRef } from 'react';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import { useReadLabelsApiLabelsGet } from './api/labels/labels';
import Select from 'react-select';
import type { MultiValue } from 'react-select';
import CreatableSelect from 'react-select/creatable';
import { useReadWordsApiWordsGet, useCreateWordApiWordsPost } from './api/words/words';
import { usePatchPhraseMeaningApiMeaningsMeaningIdPatch, usePatchPhraseMeaningExampleApiExamplesExampleIdPatch } from './api/phrases/phrases';
import { useReadPartsOfSpeechApiPartsOfSpeechGet } from './api/parts-of-speech/parts-of-speech';
import { CASES, LEVELS } from './constants';
import axios from 'axios';

function useSearchParams() {
    return new URLSearchParams(useLocation().search);
}

const selectStyles = {
    control: (provided: any) => ({
        ...provided,
        backgroundColor: '#fff',
        color: '#222',
        borderColor: '#ccc',
    }),
    menu: (provided: any) => ({
        ...provided,
        backgroundColor: '#fff',
        color: '#222',
    }),
    input: (provided: any) => ({
        ...provided,
        color: '#222',
    }),
    singleValue: (provided: any) => ({
        ...provided,
        color: '#222',
    }),
    multiValue: (provided: any) => ({
        ...provided,
        backgroundColor: '#e0e0e0',
        color: '#222',
    }),
    option: (provided: any, state: any) => ({
        ...provided,
        backgroundColor: state.isFocused ? '#f0f0f0' : '#fff',
        color: '#222',
    }),
};

export default function PhraseView() {
    const query = useSearchParams();
    const phraseId = Number(query.get('id'));
    const { data, isLoading, error, refetch } = useReadPhraseApiPhrasesPhraseIdGet(phraseId);
    const navigate = useNavigate();
    const deletePhraseMutation = useDeletePhraseApiPhrasesPhraseIdDelete();
    const addMeaning = useAddPhraseMeaningApiPhrasesPhraseIdMeaningsPost();
    const addExample = useAddPhraseExampleApiPhrasesPhraseIdExamplesPost();
    const updatePhrase = useUpdatePhraseApiPhrasesPhraseIdPut();
    const [newMeaning, setNewMeaning] = useState('');
    const [addingExampleMeaningId, setAddingExampleMeaningId] = useState<number | null>(null);
    const [newExample, setNewExample] = useState('');
    const [newExampleTranslation, setNewExampleTranslation] = useState('');
    const [editMode, setEditMode] = useState(false);
    const [editFields, setEditFields] = useState<any>(null);
    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();
    const { data: labelsData } = useReadLabelsApiLabelsGet();
    const { data: wordsData } = useReadWordsApiWordsGet();
    const createWordMutation = useCreateWordApiWordsPost();
    const { data: partsOfSpeechData } = useReadPartsOfSpeechApiPartsOfSpeechGet();
    const [editingMeaningId, setEditingMeaningId] = useState<number | null>(null);
    const [editingMeaningText, setEditingMeaningText] = useState('');
    const [editingExampleId, setEditingExampleId] = useState<number | null>(null);
    const [editingExampleText, setEditingExampleText] = useState('');
    const [editingExampleTranslation, setEditingExampleTranslation] = useState('');
    const [originalMeaningText, setOriginalMeaningText] = useState('');
    const [originalExampleText, setOriginalExampleText] = useState('');
    const [originalExampleTranslation, setOriginalExampleTranslation] = useState('');
    const prevPhraseRef = useRef<any>(null);
    const patchMeaning = usePatchPhraseMeaningApiMeaningsMeaningIdPatch();
    const patchExample = usePatchPhraseMeaningExampleApiExamplesExampleIdPatch();

    useEffect(() => {
        
        if (editingMeaningId !== null && data && Array.isArray(data.data.meanings)) {
            const oldMeaning = prevPhraseRef.current?.data?.meanings?.find((m: any) => m.id === editingMeaningId);
            const currentMeaning = data.data.meanings.find((m: any) => m.meaning === oldMeaning?.meaning);
            if (!currentMeaning) {
                setEditingMeaningId(null);
                setEditingMeaningText('');
                if (oldMeaning) alert('Це значення було змінено або видалено. Будь ласка, виберіть його заново.');
            } else if (currentMeaning.id !== editingMeaningId) {
                setEditingMeaningId(currentMeaning.id);
            }
        }
        
        if (editingExampleId !== null && data && Array.isArray(data.data.meanings)) {
            let found = false;
            for (const m of data.data.meanings) {
                const oldMeaning = prevPhraseRef.current?.data?.meanings?.find((mm: any) => mm.examples?.some((ex: any) => ex.id === editingExampleId));
                const oldExample = oldMeaning?.examples?.find((ex: any) => ex.id === editingExampleId);
                if (!oldExample) continue;
                const currentMeaning = data.data.meanings.find((mm: any) => mm.meaning === oldMeaning.meaning);
                if (!currentMeaning) continue;
                const currentExample = currentMeaning.examples?.find((ex: any) => ex.example_text === oldExample.example_text && ex.example_text_german === oldExample.example_text_german);
                if (!currentExample) {
                    setEditingExampleId(null);
                    setEditingExampleText('');
                    setEditingExampleTranslation('');
                    alert('Цей приклад був змінений або видалений. Будь ласка, виберіть його заново.');
                } else if (currentExample.id !== editingExampleId) {
                    setEditingExampleId(currentExample.id);
                }
                found = true;
                break;
            }
            if (!found && editingExampleId !== null) {
                setEditingExampleId(null);
                setEditingExampleText('');
                setEditingExampleTranslation('');
            }
        }
        prevPhraseRef.current = data;
        
    }, [data]);

    const deleteExample = async (exampleId: number) => {
        await axios.delete(`/examples/${exampleId}`);
    };

    const updateExample = async (exampleId: number, data: any) => {
        await patchExample.mutateAsync({ exampleId, data });
        refetch();
    };

    const updateMeaning = async (meaningId: number, data: any) => {
        await patchMeaning.mutateAsync({ meaningId, data });
        refetch();
    };

    const saveMeaning = async (meaningId: number, text: string) => {
        try {
            await updateMeaning(meaningId, { meaning: text });
            setEditingMeaningId(null);
            setEditingMeaningText('');
            setOriginalMeaningText('');
        } catch (err: any) {
            if (err?.response?.status === 404) {
                await refetch();
                const newMeaning = data?.data?.meanings?.find((m: any) => m.meaning === originalMeaningText);
                if (newMeaning) {
                    await updateMeaning(newMeaning.id, { meaning: text });
                    setEditingMeaningId(null);
                    setEditingMeaningText('');
                    setOriginalMeaningText('');
                } else {
                    setEditingMeaningId(null);
                    setEditingMeaningText('');
                    setOriginalMeaningText('');
                    alert('Це значення було видалено або змінено. Будь ласка, виберіть його заново.');
                }
            } else {
                alert('Помилка при оновленні значення.');
            }
        }
    };

    const saveExample = async (exampleId: number, meaning: any, text: string, translation: string) => {
        try {
            await updateExample(exampleId, {
                phrase_meaning_id: meaning.id,
                example_text: text,
                example_text_german: translation,
            });
            setEditingExampleId(null);
            setEditingExampleText('');
            setEditingExampleTranslation('');
            setOriginalExampleText('');
            setOriginalExampleTranslation('');
        } catch (err: any) {
            if (err?.response?.status === 404) {
                await refetch();
                const newMeaning = data?.data?.meanings?.find((m: any) => m.meaning === meaning.meaning);
                if (!newMeaning) {
                    setEditingExampleId(null);
                    setEditingExampleText('');
                    setEditingExampleTranslation('');
                    setOriginalExampleText('');
                    setOriginalExampleTranslation('');
                    alert('Цей приклад був видалений або змінений. Будь ласка, виберіть його заново.');
                    return;
                }
                const newExample = newMeaning.examples?.find((ex: any) => ex.example_text === originalExampleText && ex.example_text_german === originalExampleTranslation);
                if (newExample) {
                    await updateExample(newExample.id, {
                        phrase_meaning_id: newMeaning.id,
                        example_text: text,
                        example_text_german: translation,
                    });
                    setEditingExampleId(null);
                    setEditingExampleText('');
                    setEditingExampleTranslation('');
                    setOriginalExampleText('');
                    setOriginalExampleTranslation('');
                    return;
                } else {
                    setEditingExampleId(null);
                    setEditingExampleText('');
                    setEditingExampleTranslation('');
                    setOriginalExampleText('');
                    setOriginalExampleTranslation('');
                    alert('Цей приклад був видалений або змінений. Будь ласка, виберіть його заново.');
                    return;
                }
            } else {
                alert('Помилка при оновленні прикладу.');
            }
        }
    };

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error loading phrase.</div>;
    if (!data?.data) return <div>Phrase not found.</div>;
    const phrase = data.data;

    
    const handleEditChange = (field: string, value: any) => {
        setEditFields((prev: any) => ({ ...prev, [field]: value }));
    };
    const handleMultiSelectChange = (field: string, values: any[]) => {
        setEditFields((prev: any) => ({ ...prev, [field]: values }));
    };
    const handleEditStart = () => {
        
        if (!labelsData?.data || !categoriesData?.data || !wordsData?.data) {
            alert('Дані ще завантажуються. Спробуйте ще раз через декілька секунд.');
            return;
        }
        
        let labelIds: number[] = [];
        if (Array.isArray(phrase.labels) && labelsData?.data) {
            labelIds = phrase.labels.map((name: string) => {
                const found = labelsData.data.find((l: any) => l.name === name);
                return found ? found.id : null;
            }).filter((id: number | null) => id !== null);
        }
        setEditFields({
            words: phrase.words.map((w: any) => ({ value: w.id, label: w.text })),
            level: phrase.level ?? '',
            frequency: phrase.frequency ?? '',
            categories: Array.isArray(phrase.categories) ? phrase.categories : [],
            labels: labelIds,
        });
        setEditMode(true);
    };
    const handleEditSave = async () => {
        const labelNames = Array.isArray(editFields.labels) && labelsData?.data
            ? labelsData.data.filter((label: any) => editFields.labels.includes(label.id)).map((label: any) => label.name)
            : [];
        const payload = {
            words: Array.isArray(editFields.words) ? editFields.words.map((w: any) => w.value) : [],
            level: editFields.level,
            frequency: editFields.frequency,
            categories: editFields.categories,
            labels: labelNames,
        };
        console.log('Отправляю на сервер:', payload);
        await updatePhrase.mutateAsync({
            phraseId: phrase.id,
            data: payload,
        });
        setEditMode(false);
        refetch();
    };
    const handleEditCancel = () => {
        setEditMode(false);
        setEditFields(null);
    };

    return (
        <div>
            <h2>Деталі фрази</h2>
            {editMode ? (
                <div style={{ marginBottom: 16 }}>
                    <div><strong>Слова:</strong>
                        <CreatableSelect
                            isMulti
                            styles={selectStyles}
                            options={wordsData?.data?.map((word: any) => ({ value: word.id, label: word.text })) || []}
                            value={editFields.words}
                            onChange={async (selected, actionMeta) => {
                                if (actionMeta.action === 'create-option' && selected) {
                                    const newOption = selected[selected.length - 1];
                                    let partOfSpeechId = 1;
                                    if (partsOfSpeechData?.data?.length) partOfSpeechId = partsOfSpeechData.data[0].id;
                                    try {
                                        const res = await createWordMutation.mutateAsync({ data: { text: newOption.label, case: CASES[0], part_of_speech: partOfSpeechId } });
                                        const newWord = res.data;
                                        setEditFields((prev: any) => ({ ...prev, words: [...selected.slice(0, -1), { value: newWord.id, label: newWord.text }] }));
                                    } catch (e) {
                                        setEditFields((prev: any) => ({ ...prev, words: selected.slice(0, -1) }));
                                    }
                                } else {
                                    setEditFields((prev: any) => ({ ...prev, words: selected }));
                                }
                            }}
                        />
                    </div>
                    <div><strong>Рівень:</strong>
                        <select value={editFields.level} onChange={e => handleEditChange('level', e.target.value)}>
                            <option value="">—</option>
                            {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                        </select>
                    </div>
                    <div><strong>Частота:</strong> <input value={editFields.frequency} onChange={e => handleEditChange('frequency', e.target.value)} /></div>
                    <div><strong>Категорії:</strong>
                        <Select
                            isMulti
                            styles={selectStyles}
                            options={categoriesData?.data?.map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                            value={categoriesData?.data?.filter((cat: any) => editFields.categories.includes(cat.id)).map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                            onChange={(selected: MultiValue<{ value: number; label: string }>) => handleMultiSelectChange('categories', selected.map(opt => opt.value))}
                        />
                    </div>
                    <div><strong>Мітки:</strong>
                        <Select
                            isMulti
                            styles={selectStyles}
                            options={labelsData?.data?.map((label: any) => ({ value: label.id, label: label.name })) || []}
                            value={labelsData?.data?.filter((label: any) => editFields.labels.includes(label.id)).map((label: any) => ({ value: label.id, label: label.name })) || []}
                            onChange={(selected: MultiValue<{ value: number; label: string }>) => handleMultiSelectChange('labels', selected.map(opt => opt.value))}
                        />
                    </div>
                    <button onClick={handleEditSave}>Зберегти</button>
                    <button onClick={handleEditCancel}>Скасувати</button>
                </div>
            ) : null}
            <div><strong>ID:</strong> {phrase.id}</div>
            <div><strong>Слова:</strong> {phrase.words && Array.isArray(phrase.words) ? phrase.words.map((w: any) => w.text).join(' ') : '—'}</div>
            <div><strong>Мітки:</strong> {phrase.labels && phrase.labels.length > 0 ? phrase.labels.join(', ') : '—'}</div>
            <div><strong>Рівень:</strong> {phrase.level ?? '—'}</div>
            <div><strong>Частота:</strong> {phrase.frequency ?? '—'}</div>
            <div><strong>Категорії:</strong> {
                Array.isArray(phrase.categories ?? []) && categoriesData?.data
                    ? categoriesData.data.filter((cat: any) => (phrase.categories ?? []).includes(cat.id)).map((cat: any) => cat.name).join(', ')
                    : '—'
            }</div>
            <div><strong>Кількість слів:</strong> {phrase.word_count}</div>
            <div><strong>Кількість значень:</strong> {phrase.value_count}</div>
            <div><strong>Значення:</strong>
                <ul>
                    {(Array.isArray(phrase.meanings) ? phrase.meanings : []).map((meaning: any) => (
                        <li key={meaning.id}>
                            <div>
                                {editingMeaningId === meaning.id ? (
                                    <>
                                        <input
                                            value={editingMeaningText}
                                            onChange={e => setEditingMeaningText(e.target.value)}
                                            style={{ marginRight: 8 }}
                                        />
                                        <button
                                            onClick={() => saveMeaning(meaning.id, editingMeaningText)}
                                            style={{ marginRight: 8 }}
                                        >Зберегти</button>
                                        <button onClick={() => { setEditingMeaningId(null); setEditingMeaningText(''); }}>Скасувати</button>
                                    </>
                                ) : (
                                    <>
                                        <span>Значення: {meaning.meaning}</span>
                                        <IsAdmin>
                                            <button style={{ marginLeft: 8 }} onClick={() => { setEditingMeaningId(meaning.id); setEditingMeaningText(meaning.meaning); setOriginalMeaningText(meaning.meaning); }}>Редагувати</button>
                                        </IsAdmin>
                                    </>
                                )}
                            </div>
                            <div>Приклади:
                                <ul>
                                    {(Array.isArray(meaning.examples) ? meaning.examples : []).map((example: any) => (
                                        <li key={example.id}>
                                            {editingExampleId === example.id ? (
                                                <>
                                                    <input
                                                        value={editingExampleText}
                                                        onChange={e => setEditingExampleText(e.target.value)}
                                                        placeholder="Приклад"
                                                        style={{ marginRight: 8 }}
                                                    />
                                                    <input
                                                        value={editingExampleTranslation}
                                                        onChange={e => setEditingExampleTranslation(e.target.value)}
                                                        placeholder="Переклад (німецька)"
                                                        style={{ marginRight: 8 }}
                                                    />
                                                    <button
                                                        onClick={() => saveExample(example.id, meaning, editingExampleText, editingExampleTranslation)}
                                                        style={{ marginRight: 8 }}
                                                    >Зберегти</button>
                                                    <button onClick={() => { setEditingExampleId(null); setEditingExampleText(''); setEditingExampleTranslation(''); }}>Скасувати</button>
                                                </>
                                            ) : (
                                                <>
                                                    <span>{example.example_text}</span>
                                                    {example.example_text_german && (
                                                        <span style={{ color: '#888', marginLeft: 8 }}>({example.example_text_german})</span>
                                                    )}
                                                    <IsAdmin>
                                                        <button style={{ marginLeft: 8 }} onClick={() => { setEditingExampleId(example.id); setEditingExampleText(example.example_text); setEditingExampleTranslation(example.example_text_german || ''); setOriginalExampleText(example.example_text); setOriginalExampleTranslation(example.example_text_german || ''); }}>Редагувати</button>
                                                        <button
                                                            style={{ marginLeft: 4 }}
                                                            onClick={async () => {
                                                                if (window.confirm('Видалити цей приклад?')) {
                                                                    await deleteExample(example.id);
                                                                    refetch();
                                                                }
                                                            }}
                                                            disabled={false}
                                                        >Видалити</button>
                                                    </IsAdmin>
                                                </>
                                            )}
                                        </li>
                                    ))}
                                    {addingExampleMeaningId === meaning.id && (
                                        <li>
                                            <input
                                                value={newExample}
                                                onChange={e => setNewExample(e.target.value)}
                                                placeholder="Новий приклад"
                                                style={{ marginRight: 8 }}
                                            />
                                            <input
                                                value={newExampleTranslation}
                                                onChange={e => setNewExampleTranslation(e.target.value)}
                                                placeholder="Переклад (німецька)"
                                                style={{ marginRight: 8 }}
                                            />
                                            <button
                                                onClick={async () => {
                                                    await addExample.mutateAsync({ phraseId: phrase.id, data: { phrase_meaning_id: meaning.id, example_text: newExample, example_text_german: newExampleTranslation } });
                                                    setNewExample('');
                                                    setNewExampleTranslation('');
                                                    setAddingExampleMeaningId(null);
                                                    refetch();
                                                }}
                                            >Додати</button>
                                            <button onClick={() => { setAddingExampleMeaningId(null); setNewExample(''); setNewExampleTranslation(''); }}>Скасувати</button>
                                        </li>
                                    )}
                                </ul>
                                <IsAdmin>
                                    <button style={{ marginTop: 4 }} onClick={() => setAddingExampleMeaningId(meaning.id)}>Додати приклад</button>
                                </IsAdmin>
                            </div>
                        </li>
                    ))}
                </ul>
                <IsAdmin>
                    <div style={{ marginTop: 8 }}>
                        <input
                            value={newMeaning}
                            onChange={e => setNewMeaning(e.target.value)}
                            placeholder="Нове значення"
                            style={{ marginRight: 8 }}
                        />
                        <button
                            onClick={async () => {
                                if (!newMeaning.trim()) return;
                                await addMeaning.mutateAsync({ phraseId: phrase.id, data: { meaning: newMeaning } });
                                setNewMeaning('');
                                refetch();
                            }}
                        >Додати значення</button>
                    </div>
                </IsAdmin>
            </div>
            <IsAdmin>
                <div style={{ marginTop: 16 }}>
                    <button
                        onClick={handleEditStart}
                        style={{ marginRight: 8 }}
                        disabled={
                            !labelsData?.data ||
                            !categoriesData?.data ||
                            !wordsData?.data
                        }
                    >Редагувати</button>
                    <button
                        onClick={() => {
                            if (window.confirm('Ви впевнені, що хочете видалити цю фразу?')) {
                                deletePhraseMutation.mutate({ phraseId: phrase.id }, {
                                    onSuccess: () => navigate('/reference')
                                });
                            }
                        }}
                        disabled={deletePhraseMutation.isPending}
                        style={{ color: 'red' }}
                    >Видалити</button>
                </div>
            </IsAdmin>
        </div>
    );
} 
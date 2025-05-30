import { useReadWordApiWordsWordIdGet, useAddWordMeaningApiWordsWordIdMeaningsPost, usePatchWordMeaningApiWordsMeaningsMeaningIdPatch, useDeleteWordMeaningApiWordsMeaningsMeaningIdDelete, useAddWordMeaningExampleApiWordsMeaningsMeaningIdExamplesPost, usePatchWordMeaningExampleApiWordsExamplesExampleIdPatch, useDeleteWordMeaningExampleApiWordsExamplesExampleIdDelete, useDeleteWordApiWordsWordIdDelete } from './api/words/words';
import { useLocation, useNavigate } from 'react-router-dom';
import IsAdmin from './IsAdmin';
import { useState, useRef, useEffect } from 'react';
import { useAddWordComponentApiWordsWordIdComponentsPost, useUpdateWordComponentApiComponentsComponentIdPut, useDeleteWordComponentApiComponentsComponentIdDelete, useListWordComponentsApiComponentsGet, useDeleteWordComponentLinkApiWordsWordIdComponentsComponentIdDelete } from './api/components/components';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import CreatableSelect from 'react-select/creatable';

function useSearchParams() {
    return new URLSearchParams(useLocation().search);
}


const COMPONENT_TYPES = ['prefix', 'root', 'suffix', 'infix', 'postfix', 'other'];

export default function WordView() {
    const query = useSearchParams();
    const wordId = Number(query.get('id'));
    const { data, isLoading, error, refetch } = useReadWordApiWordsWordIdGet(wordId);
    const navigate = useNavigate();
    const deleteWordMutation = useDeleteWordApiWordsWordIdDelete();

    
    const [newMeaning, setNewMeaning] = useState('');
    const [editingMeaningId, setEditingMeaningId] = useState<number | null>(null);
    const [editingMeaningText, setEditingMeaningText] = useState('');
    const [originalMeaningText, setOriginalMeaningText] = useState('');

    
    const [addingExampleMeaningId, setAddingExampleMeaningId] = useState<number | null>(null);
    const [newExample, setNewExample] = useState('');
    const [newExampleTranslation, setNewExampleTranslation] = useState('');
    const [editingExampleId, setEditingExampleId] = useState<number | null>(null);
    const [editingExampleText, setEditingExampleText] = useState('');
    const [editingExampleTranslation, setEditingExampleTranslation] = useState('');
    const [originalExampleText, setOriginalExampleText] = useState('');
    const [originalExampleTranslation, setOriginalExampleTranslation] = useState('');

    
    const [newComponent, setNewComponent] = useState({ type: '', text: '', order: 0, meanings: [] as string[] });
    const [editingComponentId, setEditingComponentId] = useState<number | null>(null);
    const [editingComponent, setEditingComponent] = useState({ type: '', text: '', order: 0 });

    
    const [editingComponentMeaningIdx, setEditingComponentMeaningIdx] = useState<{ componentId: number, idx: number } | null>(null);
    const [editingComponentMeaningText, setEditingComponentMeaningText] = useState('');
    const [addingComponentMeaningId, setAddingComponentMeaningId] = useState<number | null>(null);
    const [newComponentMeaning, setNewComponentMeaning] = useState('');

    
    const addMeaning = useAddWordMeaningApiWordsWordIdMeaningsPost();
    const patchMeaning = usePatchWordMeaningApiWordsMeaningsMeaningIdPatch();
    const deleteMeaning = useDeleteWordMeaningApiWordsMeaningsMeaningIdDelete();
    
    const addExample = useAddWordMeaningExampleApiWordsMeaningsMeaningIdExamplesPost();
    const patchExample = usePatchWordMeaningExampleApiWordsExamplesExampleIdPatch();
    const deleteExample = useDeleteWordMeaningExampleApiWordsExamplesExampleIdDelete();
    
    const addComponent = useAddWordComponentApiWordsWordIdComponentsPost();
    const updateComponent = useUpdateWordComponentApiComponentsComponentIdPut();
    const deleteComponent = useDeleteWordComponentApiComponentsComponentIdDelete();

    
    const { data: allComponentsData } = useListWordComponentsApiComponentsGet();
    const allComponents = allComponentsData?.data?.items || [];
    const [componentTextSuggestions, setComponentTextSuggestions] = useState<any[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();

    const prevWordRef = useRef<any>(null);

    useEffect(() => {
        if (editingExampleId !== null && data && Array.isArray(data.data.meanings)) {
            let found = false;
            for (const m of data.data.meanings) {
                const oldMeaning = prevWordRef.current?.data?.meanings?.find((mm: any) => mm.examples?.some((ex: any) => ex.id === editingExampleId));
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
        prevWordRef.current = data;
    }, [data]);

    useEffect(() => {
        
        if (editingMeaningId !== null && data && Array.isArray(data.data.meanings)) {
            const oldMeaning = prevWordRef.current?.data?.meanings?.find((m: any) => m.id === editingMeaningId);
            const currentMeaning = data.data.meanings.find((m: any) => m.meaning === oldMeaning?.meaning);
            if (!currentMeaning) {
                setEditingMeaningId(null);
                setEditingMeaningText('');
                if (oldMeaning) alert('Це значення було змінено або видалено. Будь ласка, виберіть його заново.');
            } else if (currentMeaning.id !== editingMeaningId) {
                setEditingMeaningId(currentMeaning.id);
            }
        }
        prevWordRef.current = data;
    }, [data]);

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error loading word.</div>;
    if (!data?.data) return <div>Word not found.</div>;
    const word = data.data;
    const partOfSpeechName = word.part_of_speech_obj ? word.part_of_speech_obj.name : '';

    
    const getComponentOrder = (component: any) => typeof component.order === 'number' ? component.order : (editingComponent.order ?? 0);

    const saveMeaning = async (meaningId: number, text: string) => {
        console.log('[saveMeaning] PATCH meaningId:', meaningId, 'text:', text);
        try {
            await patchMeaning.mutateAsync({ meaningId, data: { meaning: text } });
            console.log('[saveMeaning] PATCH success for meaningId:', meaningId);
            setEditingMeaningId(null);
            setEditingMeaningText('');
            setOriginalMeaningText('');
            refetch();
        } catch (err: any) {
            console.error('[saveMeaning] PATCH error:', err);
            if (err?.response?.status === 404) {
                const { data: refetchedData } = await refetch();
                console.log('[saveMeaning] meanings after refetch', refetchedData?.data?.meanings);
                let newMeaning = refetchedData?.data?.meanings?.find((m: any) => m.id === meaningId);
                if (!newMeaning) {
                    newMeaning = refetchedData?.data?.meanings?.find((m: any) => m.meaning === originalMeaningText);
                }
                console.log('[saveMeaning] newMeaning found:', newMeaning);
                if (newMeaning) {
                    try {
                        await patchMeaning.mutateAsync({ meaningId: newMeaning.id, data: { meaning: text } });
                        console.log('[saveMeaning] PATCH retry success for newMeaningId:', newMeaning.id);
                        setEditingMeaningId(null);
                        setEditingMeaningText('');
                        setOriginalMeaningText('');
                        refetch();
                    } catch (err2: any) {
                        console.error('[saveMeaning] PATCH retry error:', err2);
                        setEditingMeaningId(null);
                        setEditingMeaningText('');
                        setOriginalMeaningText('');
                        alert('Помилка при повторному оновленні значення.');
                    }
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

    const saveExample = async (exampleId: number, meaningId: number, text: string, translation: string) => {
        console.log('[saveExample] PATCH exampleId:', exampleId, 'meaningId:', meaningId, 'text:', text, 'translation:', translation);
        try {
            await patchExample.mutateAsync({ exampleId, data: { example_text: text, example_text_german: translation } });
            console.log('[saveExample] PATCH success for exampleId:', exampleId);
            setEditingExampleId(null);
            setEditingExampleText('');
            setEditingExampleTranslation('');
            setOriginalExampleText('');
            setOriginalExampleTranslation('');
            refetch();
        } catch (err: any) {
            console.error('[saveExample] PATCH error:', err);
            if (err?.response?.status === 404) {
                const { data: refetchedData } = await refetch();
                console.log('[saveExample] meanings after refetch', refetchedData?.data?.meanings);
                let newMeaning = refetchedData?.data?.meanings?.find((m: any) => m.id === meaningId);
                if (!newMeaning) {
                    newMeaning = refetchedData?.data?.meanings?.find((m: any) => m.meaning === originalExampleText);
                }
                console.log('[saveExample] newMeaning found:', newMeaning);
                if (!newMeaning) {
                    setEditingExampleId(null);
                    setEditingExampleText('');
                    setEditingExampleTranslation('');
                    setOriginalExampleText('');
                    setOriginalExampleTranslation('');
                    alert('Цей приклад був видалений або змінений. Будь ласка, виберіть його заново.');
                    return;
                }
                console.log('[saveExample] examples in newMeaning:', newMeaning.examples);
                let newExample = newMeaning.examples?.find((ex: any) => ex.id === exampleId);
                if (!newExample) {
                    newExample = newMeaning.examples?.find((ex: any) => ex.example_text === originalExampleText && ex.example_text_german === originalExampleTranslation);
                }
                console.log('[saveExample] newExample found:', newExample);
                if (newExample) {
                    try {
                        await patchExample.mutateAsync({ exampleId: newExample.id, data: { example_text: text, example_text_german: translation } });
                        console.log('[saveExample] PATCH retry success for newExampleId:', newExample.id);
                        setEditingExampleId(null);
                        setEditingExampleText('');
                        setEditingExampleTranslation('');
                        setOriginalExampleText('');
                        setOriginalExampleTranslation('');
                        refetch();
                        return;
                    } catch (err2: any) {
                        console.error('[saveExample] PATCH retry error:', err2);
                        setEditingExampleId(null);
                        setEditingExampleText('');
                        setEditingExampleTranslation('');
                        setOriginalExampleText('');
                        setOriginalExampleTranslation('');
                        alert('Помилка при повторному оновленні прикладу.');
                        return;
                    }
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

    return (
        <div>
            <h2>Деталі слова</h2>
            <div style={{ border: '2px solid #bdbdbd', borderRadius: 8, padding: 16, marginBottom: 24 }}>
                <div><strong>ID:</strong>{word.id}</div>
                <div><strong>Текст: </strong>{word.text}</div>
                <div><strong>Рефлексивність: </strong>{String(word.reflexivity)}</div>
                <div><strong>Відмінок: </strong>{word.case}</div>
                <div><strong>Частина мови: </strong> {partOfSpeechName}</div>
                <div><strong>Категорія: </strong>{
                    Array.isArray(word.categories ?? []) && categoriesData?.data
                        ? categoriesData.data.filter((cat: any) => (word.categories ?? []).includes(cat.id)).map((cat: any) => cat.name).join(', ')
                        : (Array.isArray(word.category_names) && word.category_names.length > 0 ? word.category_names.join(', ') : '—')
                }</div>
                <div><strong>Рівень: </strong>{word.level}</div>
                <div><strong>Частота: </strong>{word.frequency}</div>
                <div><strong>Рід: </strong>{word.gender}</div>
                <div><strong>Множина: </strong>{word.plural_form}</div>
                <div><strong>Форма дієслова 2: </strong>{word.verb_form2}</div>
                <div><strong>Форма дієслова 3: </strong>{word.verb_form3}</div>
                <div><strong>Кількість компонентів: </strong>{word.component_count}</div>
                <div><strong>Кількість значень: </strong>{word.value_count}</div>
                <IsAdmin>
                    <button onClick={() => navigate(`/word-form?id=${word.id}`)} style={{ marginRight: 8 }}>Редагувати слово</button>
                    <button
                        onClick={() => {
                            if (window.confirm('Ви впевнені, що хочете видалити це слово?')) {
                                deleteWordMutation.mutate({ wordId: word.id }, {
                                    onSuccess: () => navigate('/reference')
                                });
                            }
                        }}
                        disabled={deleteWordMutation.isPending}
                        style={{ color: 'red' }}
                    >Видалити</button>
                </IsAdmin>
            </div>
            <div style={{ border: '2px solid #90caf9', borderRadius: 8, padding: 16, marginBottom: 24 }}>
                <strong>Компоненти: </strong>
                <ul>
                    {word.components.map(component => (
                        <li key={component.id} style={{ marginBottom: 12 }}>
                            {editingComponentId === component.id ? (
                                <>
                                    <input
                                        value={editingComponent.type}
                                        onChange={e => setEditingComponent(c => ({ ...c, type: e.target.value }))}
                                        placeholder="Тип"
                                        style={{ marginRight: 8 }}
                                    />
                                    <input
                                        value={editingComponent.text}
                                        onChange={e => setEditingComponent(c => ({ ...c, text: e.target.value }))}
                                        placeholder="Текст"
                                        style={{ marginRight: 8 }}
                                    />
                                    <input
                                        type="number"
                                        value={editingComponent.order}
                                        onChange={e => setEditingComponent(c => ({ ...c, order: Number(e.target.value) }))}
                                        placeholder="Порядок"
                                        style={{ marginRight: 8, width: 60 }}
                                    />
                                    <button
                                        onClick={async () => {
                                            await updateComponent.mutateAsync({ componentId: component.id, data: { ...component, meanings: component.meanings.map((m: any) => m.meaning), order: getComponentOrder(component) } });
                                            setEditingComponentId(null);
                                            setEditingComponent({ type: '', text: '', order: 0 });
                                            refetch();
                                        }}
                                    >Зберегти</button>
                                    <button onClick={() => { setEditingComponentId(null); setEditingComponent({ type: '', text: '', order: 0 }); }}>Скасувати</button>
                                </>
                            ) : (
                                <>
                                    <div>Тип: {component.type}</div>
                                    <div>Текст: {component.text}</div>
                                    <div>Кількість значень: {component.value_count}</div>
                                    <IsAdmin>
                                        <button style={{ marginRight: 4 }} onClick={() => { setEditingComponentId(component.id); setEditingComponent({ type: component.type, text: component.text, order: 0 }); }}>Редагувати</button>
                                        <button style={{ marginRight: 4 }} onClick={async () => { 
                                            await useDeleteWordComponentLinkApiWordsWordIdComponentsComponentIdDelete().mutateAsync({ wordId, componentId: component.id }); 
                                            refetch(); 
                                        }}>Видалити</button>
                                    </IsAdmin>
                                </>
                            )}
                            <div>Значення:
                                <ul>
                                    {component.meanings.map((meaningObj, idx) => (
                                        <li key={meaningObj.id}>
                                            {editingComponentMeaningIdx && editingComponentMeaningIdx.componentId === component.id && editingComponentMeaningIdx.idx === idx ? (
                                                <>
                                                    <input
                                                        value={editingComponentMeaningText}
                                                        onChange={e => setEditingComponentMeaningText(e.target.value)}
                                                        style={{ marginRight: 8 }}
                                                    />
                                                    <button
                                                        onClick={async () => {
                                                            const newMeanings = component.meanings.map((m, i) => i === idx ? editingComponentMeaningText : m.meaning);
                                                            await updateComponent.mutateAsync({ componentId: component.id, data: { ...component, meanings: newMeanings, order: getComponentOrder(component) } });
                                                            setEditingComponentMeaningIdx(null);
                                                            setEditingComponentMeaningText('');
                                                            refetch();
                                                        }}
                                                    >Зберегти</button>
                                                    <button onClick={() => { setEditingComponentMeaningIdx(null); setEditingComponentMeaningText(''); }}>Скасувати</button>
                                                </>
                                            ) : (
                                                <>
                                                    <span>{meaningObj.meaning}</span>
                                                    <IsAdmin>
                                                        <button style={{ marginLeft: 8 }} onClick={() => { setEditingComponentMeaningIdx({ componentId: component.id, idx }); setEditingComponentMeaningText(meaningObj.meaning); }}>Редагувати</button>
                                                        <button style={{ marginLeft: 4 }} onClick={async () => {
                                                            const newMeanings = component.meanings.filter((_, i) => i !== idx).map(m => m.meaning);
                                                            await updateComponent.mutateAsync({ componentId: component.id, data: { ...component, meanings: newMeanings, order: getComponentOrder(component) } });
                                                            refetch();
                                                        }}>Видалити</button>
                                                    </IsAdmin>
                                                </>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                                <IsAdmin>
                                    {addingComponentMeaningId === component.id ? (
                                        <>
                                            <input
                                                value={newComponentMeaning}
                                                onChange={e => setNewComponentMeaning(e.target.value)}
                                                placeholder="Нове значення"
                                                style={{ marginRight: 8 }}
                                            />
                                            <button
                                                onClick={async () => {
                                                    const newMeanings = [...component.meanings.map(m => m.meaning), newComponentMeaning];
                                                    await updateComponent.mutateAsync({ componentId: component.id, data: { ...component, meanings: newMeanings, order: getComponentOrder(component) } });
                                                    setNewComponentMeaning('');
                                                    setAddingComponentMeaningId(null);
                                                    refetch();
                                                }}
                                            >Додати</button>
                                            <button onClick={() => { setAddingComponentMeaningId(null); setNewComponentMeaning(''); }}>Скасувати</button>
                                        </>
                                    ) : (
                                        <button onClick={() => setAddingComponentMeaningId(component.id)}>Додати значення</button>
                                    )}
                                </IsAdmin>
                            </div>
                        </li>
                    ))}
                </ul>
                <IsAdmin>
                    <div style={{ marginTop: 8, position: 'relative', maxWidth: 400, display: 'flex', gap: 8, alignItems: 'center' }}>
                        <select
                            value={newComponent.type}
                            onChange={e => setNewComponent(c => ({ ...c, type: e.target.value }))}
                            style={{ minWidth: 100 }}
                        >
                            <option value="">Тип</option>
                            {COMPONENT_TYPES.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                        <div style={{ flex: 1 }}>
                            <CreatableSelect
                                isClearable
                                options={allComponents.map((comp: any) => ({ value: comp.id, label: comp.text }))}
                                onChange={async (option: any, actionMeta: any) => {
                                    if (!option) return;
                                    if (actionMeta.action === 'create-option') {
                                        if (!newComponent.type) return; 
                                        
                                        const created = await addComponent.mutateAsync({
                                            wordId,
                                            data: { type: newComponent.type, text: option.label, order: newComponent.order, meanings: [] }
                                        });
                                        setNewComponent({ type: '', text: '', order: 0, meanings: [] });
                                        refetch();
                                    } else {
                                        
                                        const comp = allComponents.find((c: any) => c.id === option.value);
                                        if (comp) {
                                            await addComponent.mutateAsync({
                                                wordId,
                                                data: { type: comp.type, text: comp.text, order: newComponent.order, meanings: comp.meanings?.map((m: any) => m.meaning) || [] }
                                            });
                                            setNewComponent({ type: '', text: '', order: 0, meanings: [] });
                                            refetch();
                                        }
                                    }
                                }}
                                placeholder="Виберіть або створіть компонент..."
                                value={null}
                                isDisabled={!newComponent.type}
                            />
                        </div>
                        <input
                            type="number"
                            value={newComponent.order}
                            onChange={e => setNewComponent(c => ({ ...c, order: Number(e.target.value) }))}
                            placeholder="Порядок"
                            style={{ width: 60 }}
                        />
                    </div>
                </IsAdmin>
            </div>
            <div style={{ border: '2px solid #a5d6a7', borderRadius: 8, padding: 16, marginBottom: 24 }}>
                <strong>Значення:</strong>
                <ul>
                    {word.meanings?.map(meaning => (
                        <li key={meaning.id} style={{ marginBottom: 12 }}>
                            <div>
                                {editingMeaningId === meaning.id ? (
                                    <>
                                        <input
                                            value={editingMeaningText}
                                            onChange={e => setEditingMeaningText(e.target.value)}
                                            style={{ marginRight: 8 }}
                                        />
                                        <button
                                            onClick={async () => {
                                                await saveMeaning(meaning.id, editingMeaningText);
                                            }}
                                        >Зберегти</button>
                                        <button onClick={() => { setEditingMeaningId(null); setEditingMeaningText(''); }}>Скасувати</button>
                                    </>
                                ) : (
                                    <>
                                        <span>Значення: {meaning.meaning}</span>
                                        <IsAdmin>
                                            <button style={{ marginLeft: 8 }} onClick={() => { setEditingMeaningId(meaning.id); setEditingMeaningText(meaning.meaning); setOriginalMeaningText(meaning.meaning); }}>Редагувати</button>
                                            <button style={{ marginLeft: 4 }} onClick={async () => { await deleteMeaning.mutateAsync({ meaningId: meaning.id }); refetch(); }}>Видалити</button>
                                        </IsAdmin>
                                    </>
                                )}
                            </div>
                            <div>Приклади:
                                <ul>
                                    {meaning.examples?.map(example => (
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
                                                        placeholder="Переклад"
                                                        style={{ marginRight: 8 }}
                                                    />
                                                    <button
                                                        onClick={async () => {
                                                            await saveExample(example.id, meaning.id, editingExampleText, editingExampleTranslation);
                                                        }}
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
                                                        <button style={{ marginLeft: 4 }} onClick={async () => { await deleteExample.mutateAsync({ exampleId: example.id }); refetch(); }}>Видалити</button>
                                                    </IsAdmin>
                                                </>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                                <IsAdmin>
                                    {addingExampleMeaningId === meaning.id ? (
                                        <>
                                            <input
                                                value={newExample}
                                                onChange={e => setNewExample(e.target.value)}
                                                placeholder="Новий приклад"
                                                style={{ marginRight: 8 }}
                                            />
                                            <input
                                                value={newExampleTranslation}
                                                onChange={e => setNewExampleTranslation(e.target.value)}
                                                placeholder="Переклад"
                                                style={{ marginRight: 8 }}
                                            />
                                            <button
                                                onClick={async () => {
                                                    await addExample.mutateAsync({ meaningId: meaning.id, data: { word_meaning_id: meaning.id, example_text: newExample, example_text_german: newExampleTranslation } });
                                                    setNewExample('');
                                                    setNewExampleTranslation('');
                                                    setAddingExampleMeaningId(null);
                                                    refetch();
                                                }}
                                            >Додати</button>
                                            <button onClick={() => { setAddingExampleMeaningId(null); setNewExample(''); setNewExampleTranslation(''); }}>Скасувати</button>
                                        </>
                                    ) : (
                                        <button onClick={() => setAddingExampleMeaningId(meaning.id)}>Додати приклад</button>
                                    )}
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
                                await addMeaning.mutateAsync({ wordId, data: { meaning: newMeaning } });
                                setNewMeaning('');
                                refetch();
                            }}
                        >Додати значення</button>
                    </div>
                </IsAdmin>
            </div>
        </div>
    );
}

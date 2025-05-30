import { useLocation } from 'react-router-dom';
import { useGetWordComponentApiComponentsComponentIdGet, useUpdateWordComponentApiComponentsComponentIdPut } from './api/components/components';
import IsAdmin from './IsAdmin';
import { useState } from 'react';

function useSearchParams() {
    return new URLSearchParams(useLocation().search);
}

const COMPONENT_TYPES = ['prefix', 'root', 'suffix', 'infix', 'postfix', 'other'];

export default function ComponentView() {
    const query = useSearchParams();
    const componentId = Number(query.get('id'));
    const { data, isLoading, error, refetch } = useGetWordComponentApiComponentsComponentIdGet(componentId);
    const updateComponent = useUpdateWordComponentApiComponentsComponentIdPut();

    const [editing, setEditing] = useState(false);
    const [type, setType] = useState('');
    const [text, setText] = useState('');
    const [meanings, setMeanings] = useState<string[]>([]);
    const [newMeaning, setNewMeaning] = useState('');
    const [editingMeaningIdx, setEditingMeaningIdx] = useState<number | null>(null);
    const [editingMeaningText, setEditingMeaningText] = useState('');

    if (isLoading) return <div>Завантаження...</div>;
    if (error) return <div>Помилка завантаження компонента.</div>;
    if (!data?.data) return <div>Компонент не знайдено.</div>;
    const component = data.data;

    
    function startEdit() {
        setType(component.type);
        setText(component.text);
        setMeanings(component.meanings.map((m: any) => m.meaning));
        setEditing(true);
    }

    async function saveEdit() {
        await updateComponent.mutateAsync({ componentId, data: { ...component, type, text, meanings, order: component.order ?? 0 } });
        setEditing(false);
        refetch();
    }

    return (
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <h2>Деталі компонента слова</h2>
            <div><strong>ID:</strong> {component.id}</div>
            {editing ? (
                <>
                    <div>
                        <label>Тип: </label>
                        <select value={type} onChange={e => setType(e.target.value)}>
                            {COMPONENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>
                    <div>
                        <label>Текст: </label>
                        <input value={text} onChange={e => setText(e.target.value)} />
                    </div>
                    <div>
                        <label>Значення:</label>
                        <ul>
                            {meanings.map((m, idx) => (
                                <li key={idx}>
                                    {editingMeaningIdx === idx ? (
                                        <>
                                            <input value={editingMeaningText} onChange={e => setEditingMeaningText(e.target.value)} />
                                            <button onClick={() => {
                                                setMeanings(meanings.map((mm, i) => i === idx ? editingMeaningText : mm));
                                                setEditingMeaningIdx(null);
                                                setEditingMeaningText('');
                                            }}>Зберегти</button>
                                            <button onClick={() => { setEditingMeaningIdx(null); setEditingMeaningText(''); }}>Скасувати</button>
                                        </>
                                    ) : (
                                        <>
                                            <span>{m}</span>
                                            <button style={{ marginLeft: 8 }} onClick={() => { setEditingMeaningIdx(idx); setEditingMeaningText(m); }}>Редагувати</button>
                                            <button style={{ marginLeft: 4 }} onClick={() => setMeanings(meanings.filter((_, i) => i !== idx))}>Видалити</button>
                                        </>
                                    )}
                                </li>
                            ))}
                        </ul>
                        <input value={newMeaning} onChange={e => setNewMeaning(e.target.value)} placeholder="Нове значення" />
                        <button onClick={() => { if (newMeaning.trim()) { setMeanings([...meanings, newMeaning]); setNewMeaning(''); } }}>Додати</button>
                    </div>
                    <button onClick={saveEdit} style={{ marginRight: 8 }}>Зберегти</button>
                    <button onClick={() => setEditing(false)}>Скасувати</button>
                </>
            ) : (
                <>
                    <div><strong>Тип:</strong> {component.type}</div>
                    <div><strong>Текст:</strong> {component.text}</div>
                    <div><strong>Значення:</strong>
                        <ul>
                            {component.meanings.map((m: any) => <li key={m.id}>{m.meaning}</li>)}
                        </ul>
                    </div>
                    <IsAdmin>
                        <button onClick={startEdit}>Редагувати</button>
                    </IsAdmin>
                </>
            )}
        </div>
    );
} 
import { useLocation } from 'react-router-dom';
import { useGetSemanticGroupApiSemanticGroupsGroupIdGet, useUpdateSemanticGroupApiSemanticGroupsGroupIdPatch } from './api/semantic-groups/semantic-groups';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import IsAdmin from './IsAdmin';
import { useState } from 'react';
import SemanticGroupForm from './SemanticGroupForm';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function useSearchParams() {
    return new URLSearchParams(useLocation().search);
}

export default function SemanticGroupView() {
    const query = useSearchParams();
    const groupId = Number(query.get('id'));
    const { data, isLoading, error, refetch } = useGetSemanticGroupApiSemanticGroupsGroupIdGet(groupId);
    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();
    const updateGroup = useUpdateSemanticGroupApiSemanticGroupsGroupIdPatch();
    const navigate = useNavigate();
    const [editMode, setEditMode] = useState(false);
    const [editStatus, setEditStatus] = useState<string | null>(null);
    const [editFields, setEditFields] = useState<any>(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [status, setStatus] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    if (isLoading) return <div>Завантаження...</div>;
    if (error) return <div>Помилка завантаження семантичної групи.</div>;
    if (!data?.data) return <div>Семантичну групу не знайдено.</div>;
    const group = data.data;

    function startEdit() {
        setEditFields({
            name: group.name ?? '',
            level: group.level ?? '',
            frequency: Number(group.frequency) ?? 0,
            categories: Array.isArray(group.categories) ? group.categories : [],
            word_ids: Array.isArray(group.words) ? group.words.map((w: any) => w.id) : [],
            phrase_ids: Array.isArray(group.phrases) ? group.phrases.map((p: any) => p.id) : [],
            explanation: group.explanation ?? '',
            difference_explanation: group.difference_explanation ?? '',
        });
        setEditMode(true);
        setStatus(null);
    }

    async function handleEditSave(fields: any) {
        setLoading(true);
        setEditStatus(null);
        updateGroup.mutate(
            {
                groupId,
                data: {
                    name: fields.name,
                    level: fields.level,
                    frequency: fields.frequency,
                    categories: fields.categories,
                    word_ids: fields.word_ids,
                    phrase_ids: fields.phrase_ids,
                    explanation: fields.explanation,
                    difference_explanation: fields.difference_explanation,
                },
            },
            {
                onSuccess: () => {
                    setEditMode(false);
                    setLoading(false);
                    setEditStatus('Збережено!');
                    refetch();
                },
                onError: (err: any) => {
                    setEditStatus('Помилка: ' + (err?.message || 'Unknown error'));
                    setLoading(false);
                },
            }
        );
    }

    async function handleDelete() {
        if (!window.confirm('Видалити цю семантичну групу?')) return;
        setDeleteLoading(true);
        try {
            await axios.delete(`/api/semantic-groups/${groupId}`);
            navigate('/');
        } catch (e: any) {
            alert('Помилка видалення: ' + (e?.message || 'Unknown error'));
        } finally {
            setDeleteLoading(false);
        }
    }

    return (
        <div>
            <h2>Деталі семантичної групи</h2>
            <IsAdmin>
                <button onClick={startEdit} style={{ marginRight: 8 }}>Редагувати</button>
                <button onClick={handleDelete} style={{ color: 'red' }} disabled={deleteLoading}>{deleteLoading ? 'Видалення...' : 'Видалити'}</button>
            </IsAdmin>
            {editMode ? (
                <div style={{ margin: '16px 0', padding: 12, border: '1px solid #eee', borderRadius: 8, background: '#fafbfc', maxWidth: 700 }}>
                    <SemanticGroupForm
                        initial={editFields}
                        submitLabel="Зберегти"
                        onSubmit={handleEditSave}
                    />
                    <button onClick={() => setEditMode(false)} disabled={loading}>Скасувати</button>
                    {loading && <span style={{ marginLeft: 12 }}>Збереження...</span>}
                    {editStatus && <span style={{ marginLeft: 12 }}>{editStatus}</span>}
                </div>
            ) : null}
            <div><strong>ID:</strong> {group.id}</div>
            <div><strong>Назва:</strong> {group.name}</div>
            <div><strong>Рівень:</strong> {group.level ?? '—'}</div>
            <div><strong>Частота:</strong> {group.frequency ?? '—'}</div>
            <div><strong>Категорії:</strong> {
                Array.isArray(group.categories ?? []) && categoriesData?.data
                    ? categoriesData.data.filter((cat: any) => (group.categories ?? []).includes(cat.id)).map((cat: any) => cat.name).join(', ')
                    : (Array.isArray(group.category_names) ? group.category_names.join(', ') : '—')
            }</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <strong>Пояснення:</strong>
                <span>
                    {group.explanation?.trim()
                        ? group.explanation
                        : <span style={{ color: '#888' }}>Пояснення відсутнє</span>}
                </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <strong>Пояснення різниці:</strong>
                <span>
                    {group.difference_explanation?.trim()
                        ? group.difference_explanation
                        : <span style={{ color: '#888' }}>Пояснення ще генерується...</span>}
                </span>
            </div>
            <div><strong>Слова:</strong> {Array.isArray(group.words ?? []) && (group.words ?? []).length > 0 ? (
                (group.words ?? []).map((w: any, idx: number) => (
                    <span key={w.id}>
                        <a href={`/word?id=${w.id}`}>{w.text}</a>{idx < (group.words ?? []).length - 1 ? ', ' : ''}
                    </span>
                ))
            ) : '—'}</div>
            <div><strong>Фрази:</strong> {Array.isArray(group.phrases ?? []) && (group.phrases ?? []).length > 0 ? (
                (group.phrases ?? []).map((p: any, idx: number) => (
                    <span key={p.id}>
                        <a href={`/phrase?id=${p.id}`}>{Array.isArray(p.words) ? p.words.map((w: any) => w.text).join(' ') : p.id}</a>{idx < (group.phrases ?? []).length - 1 ? '; ' : ''}
                    </span>
                ))
            ) : '—'}</div>
            <IsAdmin><span /></IsAdmin>
        </div>
    );
} 
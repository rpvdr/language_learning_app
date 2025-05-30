import { useReadUsersMeApiMeGet, useUpdateProfileApiMeProfilePut } from './api/users/users';
import { useEffect, useState } from 'react';
import styles from './Profile.module.css';
import formStyles from './ProfileForm.module.css';
import Select from 'react-select';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import type { MultiValue } from 'react-select';
import { LEVELS } from './constants';

export default function Profile() {
    const { data, isLoading, isError, error } = useReadUsersMeApiMeGet();
    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();

    const user = data?.data;
    const [form, setForm] = useState<{
        is_public: boolean;
        target_level: string;
        categories: number[];
        region: string;
        learning_speed: string;
        daily_minutes: string;
        desired_level: string;
        current_level: string;
        entry_test_result: null;
    }>({
        is_public: false,
        target_level: '',
        categories: [],
        region: '',
        learning_speed: '',
        daily_minutes: '',
        desired_level: '',
        current_level: '',
        entry_test_result: null,
    });

    useEffect(() => {
        if (user?.profile) {
            setForm({
                is_public: Boolean(user.profile.is_public ?? false),
                target_level: String(user.profile.target_level ?? ''),
                categories: Array.isArray(user.profile.categories) ? user.profile.categories : [],
                region: String(user.profile.region ?? ''),
                learning_speed: user.profile.learning_speed !== null && user.profile.learning_speed !== undefined ? String(user.profile.learning_speed) : '',
                daily_minutes: user.profile.daily_minutes !== null && user.profile.daily_minutes !== undefined ? String(user.profile.daily_minutes) : '',
                desired_level: String(user.profile.desired_level ?? ''),
                current_level: String(user.profile.current_level ?? ''),
                entry_test_result: null,
            });
        }
    }, [user?.profile]);

    const mutation = useUpdateProfileApiMeProfilePut();
    const isSaving = mutation.status === 'pending';
    const isSaveError = mutation.status === 'error';
    const saveError = mutation.error;
    const isSuccess = mutation.status === 'success';

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setForm(f => ({
            ...f,
            [name]: type === 'checkbox' && e.target instanceof HTMLInputElement ? e.target.checked : value
        }));
    };

    
    const rawCategories = categoriesData && 'data' in categoriesData ? categoriesData.data : categoriesData || [];
    const categoryOptions = (Array.isArray(rawCategories) ? rawCategories : []).map((cat: any) => ({
        value: cat.id,
        label: cat.name || String(cat.id)
    }));

    const handleCategoriesSelect = (selected: MultiValue<{ value: number; label: string }>) => {
        setForm(f => ({
            ...f,
            categories: selected ? selected.map((opt) => opt.value) : []
        }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate({
            data: {
                ...form,
                learning_speed: form.learning_speed !== '' ? Number(form.learning_speed) : null,
                daily_minutes: form.daily_minutes !== '' ? Number(form.daily_minutes) : null,
                entry_test_result: null,
            }
        });
    };

    if (isLoading) return <div>Loading profile...</div>;
    if (isError) return <div className={styles.error}>Error: {error?.message || 'Failed to load profile.'}</div>;

    return (
        <div className={styles.container}>
            <h2>Профіль</h2>
            {user ? (
                <>
                    <div><strong>Електронна пошта:</strong> {user.email}</div>
                    <div><strong>Ролі:</strong> {user.roles.join(', ')}</div>
                    <form className={formStyles.profileForm} onSubmit={handleSubmit}>
                        <div className={formStyles.inlineGroup}>
                            <label htmlFor="is_public">Публічний профіль:</label>
                            <input id="is_public" type="checkbox" name="is_public" checked={form.is_public} onChange={handleChange} />
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="target_level">Бажаний рівень:</label>
                            <select
                                id="target_level"
                                name="target_level"
                                value={form.target_level}
                                onChange={handleChange}
                                className={formStyles.shortInput}
                            >
                                <option value="">—</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </select>
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="region">Регіон:</label>
                            <input id="region" type="text" name="region" value={form.region} onChange={handleChange} className={formStyles.shortInput} />
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="learning_speed">Швидкість навчання:</label>
                            <input id="learning_speed" type="number" name="learning_speed" value={form.learning_speed} onChange={handleChange} className={formStyles.shortInput} />
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="daily_minutes">Хвилин на день:</label>
                            <input id="daily_minutes" type="number" name="daily_minutes" value={form.daily_minutes} onChange={handleChange} className={formStyles.shortInput} />
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="desired_level">Мета (рівень):</label>
                            <select
                                id="desired_level"
                                name="desired_level"
                                value={form.desired_level}
                                onChange={handleChange}
                                className={formStyles.shortInput}
                            >
                                <option value="">—</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </select>
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="current_level">Поточний рівень:</label>
                            <select
                                id="current_level"
                                name="current_level"
                                value={form.current_level}
                                onChange={handleChange}
                                className={formStyles.shortInput}
                            >
                                <option value="">—</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </select>
                        </div>
                        <div className={formStyles.formGroup}>
                            <label htmlFor="categories">Категорії:</label>
                            <Select
                                id="categories"
                                isMulti
                                options={categoryOptions}
                                value={categoryOptions.filter(opt => form.categories.includes(opt.value))}
                                onChange={handleCategoriesSelect}
                                classNamePrefix="react-select"
                                placeholder="Оберіть категорії..."
                            />
                        </div>
                        <div className={formStyles.submitRow}>
                            <button type="submit" disabled={isSaving}>Оновити профіль</button>
                            {isSaveError && <div className={formStyles.error}>Помилка: {saveError?.message || 'Не вдалося оновити профіль.'}</div>}
                            {isSuccess && <div className={formStyles.success}>Профіль оновлено!</div>}
                        </div>
                    </form>
                    <div>
                        <strong>Дані профілю:</strong>
                        <pre className={styles.profileData}>
                            {JSON.stringify(user.profile, null, 2)}
                        </pre>
                    </div>
                </>
            ) : (
                <div>Дані профілю не знайдено.</div>
            )}
        </div>
    );
}

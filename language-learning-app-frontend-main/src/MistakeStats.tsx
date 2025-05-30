import { useGetUserErrorsApiTrainingErrorsGet, useGetErrorStatsApiTrainingErrorStatsGet, useGetErrorStatsAllApiTrainingErrorStatsAllGet, useGetAllErrorsApiTrainingErrorsAllGet } from './api/training/training';
import { useSearchMistakesApiSearchMistakesGet } from './api/search/search';
import { useAuth } from './api/ApiConfigContext';
import styles from './MistakeStats.module.css';
import { useState } from 'react';

function extractStats(raw: any) {
    
    const base = raw && typeof raw === 'object' && 'data' in raw ? raw.data : raw;
    if (base && typeof base === 'object' && 'error_statistics' in base) {
        return base.error_statistics;
    }
    return base || {};
}

function isNotFoundError(error: any) {
    
    return error && error.response && error.response.status === 404;
}

export default function MistakeStats() {
    const { roles } = useAuth();
    const isAdmin = roles.includes('admin');
    const [showAll, setShowAll] = useState(false);

    
    const { data: allErrorsRaw, isLoading: isAllLoading, isError: isAllError, error: allError } = useGetAllErrorsApiTrainingErrorsAllGet(
        undefined,
        { query: { enabled: isAdmin && showAll, queryKey: ['all-mistakes', isAdmin, showAll] } }
    );
    const { data: allStatsRaw, isLoading: isAllStatsLoading, isError: isAllStatsError, error: allStatsError } = useGetErrorStatsAllApiTrainingErrorStatsAllGet(
        undefined,
        { query: { enabled: isAdmin && showAll, queryKey: ['all-mistakes-stats', isAdmin, showAll] } }
    );

    
    const { data, isLoading, isError, error } = useGetUserErrorsApiTrainingErrorsGet(
        {},
        { query: { enabled: !showAll, queryKey: ['user-mistakes', isAdmin, showAll] } }
    );
    const { data: statsRaw, isLoading: isStatsLoading, isError: isStatsError, error: statsError } = useGetErrorStatsApiTrainingErrorStatsGet(
        undefined,
        { query: { enabled: !showAll, queryKey: ['user-mistakes-stats', isAdmin, showAll] } }
    );

    
    const errors = isAdmin && showAll ? (allErrorsRaw?.data || []) : (data?.data || []);
    const stats = extractStats(isAdmin && showAll ? allStatsRaw : statsRaw);
    const errorTypes = stats.error_types || {};

    
    if ((isAdmin && showAll && (isAllLoading || isAllStatsLoading)) || (!showAll && (isLoading || isStatsLoading))) {
        return <div>Завантаження статистики помилок...</div>;
    }
    if ((isAdmin && showAll && (isAllError || isAllStatsError)) || (!showAll && (isError || isStatsError))) {
        
        if (isAdmin && showAll && isNotFoundError(allStatsError)) {
            return (
                <div className={styles.container}>
                    <h2>Статистика помилок</h2>
                    <div style={{ color: '#b00', marginBottom: 16 }}>Статистика для всіх користувачів недоступна</div>
                    {isAdmin && (
                        <div style={{ marginBottom: 16 }}>
                            <label style={{ cursor: 'pointer', fontWeight: 500 }}>
                                <input
                                    type="checkbox"
                                    checked={showAll}
                                    onChange={e => setShowAll(e.target.checked)}
                                    style={{ marginRight: 8 }}
                                />
                                Показати всі помилки користувачів
                            </label>
                        </div>
                    )}
                    
                    <div className={styles.tableWrapper}>
                        {errors.length === 0 ? (
                            <div>Помилок не знайдено</div>
                        ) : (
                            <table className={styles.statsTable}>
                                <thead>
                                    <tr>
                                        <th>Тип</th>
                                        <th>Тип помилки</th>
                                        <th>Ваша відповідь</th>
                                        <th>Правильна відповідь</th>
                                        <th>Пояснення</th>
                                        {isAdmin && showAll && <th>ID користувача</th>}
                                        <th>Дата</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {errors.map((err) => (
                                        <tr key={err.id}>
                                            <td>{err.item_type}</td>
                                            <td>{err.error_analysis || '-'}</td>
                                            <td>{err.user_answer}</td>
                                            <td>{err.correct_answer}</td>
                                            <td>{err.brief_explanation}</td>
                                            {isAdmin && showAll && <td>{err.user_id}</td>}
                                            <td>{new Date(err.created_at).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            );
        }
        const errMsg = (isAdmin && showAll)
            ? (allError?.message || allStatsError?.message || 'Не вдалося завантажити статистику.')
            : (error?.message || statsError?.message || 'Не вдалося завантажити статистику.');
        return <div className={styles.error}>Помилка: {errMsg}</div>;
    }

    return (
        <div className={styles.container}>
            <h2>Статистика помилок</h2>
            {isAdmin && (
                <div style={{ marginBottom: 16 }}>
                    <label style={{ cursor: 'pointer', fontWeight: 500 }}>
                        <input
                            type="checkbox"
                            checked={showAll}
                            onChange={e => setShowAll(e.target.checked)}
                            style={{ marginRight: 8 }}
                        />
                        Показати всі помилки користувачів
                    </label>
                </div>
            )}
            
            {!(isAdmin && showAll && isNotFoundError(allStatsError)) && (
                <div className={styles.statsCards}>
                    <div className={styles.statsCard}>
                        <span className={styles.label}>Всього помилок</span>
                        <span className={styles.value}>{stats.total_errors ?? '-'}</span>
                    </div>
                    <div className={styles.statsCard}>
                        <span className={styles.label}>Найпоширеніша помилка</span>
                        <span className={styles.value}>{stats.most_common_error ?? '-'}</span>
                    </div>
                    <div className={styles.statsCard}>
                        <span className={styles.label}>За типами</span>
                        <span>
                            <div className={styles.errorTypes}>
                                {Object.keys(errorTypes).length === 0 ? (
                                    <span style={{ color: '#888' }}>Немає статистики помилок!</span>
                                ) : (
                                    Object.entries(errorTypes).map(([type, count]) => (
                                        <span key={type} className={styles.errorType}>
                                            <b>{type}</b>: {count as number}
                                        </span>
                                    ))
                                )}
                            </div>
                        </span>
                    </div>
                </div>
            )}
            
            <div className={styles.tableWrapper}>
            {errors.length === 0 ? (
                    <div>Помилок не знайдено</div>
            ) : (
                    <table className={styles.statsTable}>
                    <thead>
                        <tr>
                                <th>Тип</th>
                                <th>Тип помилки</th>
                                <th>Ваша відповідь</th>
                                <th>Правильна відповідь</th>
                                <th>Пояснення</th>
                                {isAdmin && showAll && <th>ID користувача</th>}
                                <th>Дата</th>
                        </tr>
                    </thead>
                    <tbody>
                        {errors.map((err) => (
                            <tr key={err.id}>
                                <td>{err.item_type}</td>
                                    <td>{err.error_analysis || '-'}</td>
                                <td>{err.user_answer}</td>
                                <td>{err.correct_answer}</td>
                                <td>{err.brief_explanation}</td>
                                {isAdmin && showAll && <td>{err.user_id}</td>}
                                <td>{new Date(err.created_at).toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            </div>
        </div>
    );
}

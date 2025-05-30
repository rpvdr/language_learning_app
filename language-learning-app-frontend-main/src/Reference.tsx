import { useReadWordsApiWordsGet, useDeleteWordApiWordsWordIdDelete } from './api/words/words';
import { useReadPhrasesApiPhrasesGet, useDeletePhraseApiPhrasesPhraseIdDelete } from './api/phrases/phrases';
import { useNavigate } from 'react-router-dom';
import IsAdmin from './IsAdmin';
import styles from './Reference.module.css';

export default function Reference() {
    const { data, isLoading, error } = useReadWordsApiWordsGet();
    const { data: phrasesData, isLoading: isPhrasesLoading, error: phrasesError } = useReadPhrasesApiPhrasesGet();
    const deleteWordMutation = useDeleteWordApiWordsWordIdDelete();
    const deletePhraseMutation = useDeletePhraseApiPhrasesPhraseIdDelete();
    const navigate = useNavigate();

    if (isLoading) return <div>Завантаження слів...</div>;
    if (error) return <div>Помилка: {error.message}</div>;
    if (!data?.data?.length) return <div>Слів не знайдено.</div>;

    return (
        <div>
            <h2>Довідник</h2>

            <IsAdmin>
                <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
                    <button onClick={() => navigate('/word-form')} className={styles.addButton}>
                        Додати слово
                    </button>
                    <button onClick={() => navigate('/phrase-builder')} className={styles.addButton}>
                        Додати фразу
                    </button>
                    <button onClick={() => navigate('/semantic-group-form')} className={styles.addButton}>
                        Додати семантичну групу
                    </button>
                    <button onClick={() => navigate('/component-form')} className={styles.addButton}>
                        Додати компонент слова
                    </button>
                </div>
            </IsAdmin>

            <h3>Слова</h3>
            <ul>
                {data.data.map(word => (
                    <li key={word.id} className={styles.listItem}>
                        <span
                            className={styles.wordLink}
                            onClick={() => navigate(`/word?id=${word.id}`)}
                            aria-label={`Переглянути деталі для слова ${word.text}`}
                        >
                            {word.text}
                        </span>
                        <IsAdmin>
                            <button
                                onClick={() => deleteWordMutation.mutate({ wordId: word.id })}
                                disabled={deleteWordMutation.isPending}
                                className={styles.deleteButton}
                                aria-label={`Видалити слово ${word.text}`}
                            >
                                Видалити
                            </button>
                            <button
                                onClick={() => navigate(`/word-form?id=${word.id}`)}
                                className={styles.editButton}
                                aria-label={`Редагувати слово ${word.text}`}
                            >
                                Редагувати
                            </button>
                        </IsAdmin>
                    </li>
                ))}
            </ul>

            <h3>Фрази</h3>
            {isPhrasesLoading && <div>Завантаження фраз...</div>}
            {phrasesError && <div>Помилка: {phrasesError.message}</div>}
            {phrasesData?.data && (
                <ul>
                    {phrasesData.data.map(phrase => (
                        <li key={phrase.id} className={styles.listItem}>
                            <span className={styles.phraseText}>
                                {phrase.words.map(word => word.text).join(' ')}
                            </span>
                            {phrase.labels && phrase.labels.length > 0 && (
                                <span className={styles.label}>
                                    [{phrase.labels.join(', ')}]
                                </span>
                            )}
                            <IsAdmin>
                                <button
                                    onClick={() => deletePhraseMutation.mutate({ phraseId: phrase.id })}
                                    disabled={deletePhraseMutation.isPending}
                                    className={styles.deleteButton}
                                    aria-label={`Видалити фразу ${phrase.id}`}
                                >
                                    Видалити
                                </button>
                            </IsAdmin>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

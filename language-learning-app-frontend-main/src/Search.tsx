import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSearchWordsApiSearchWordsGet, useSearchPhrasesApiSearchPhrasesGet, useSearchSemanticGroupsApiSearchSemanticGroupsGet, useSearchWordComponentsApiSearchWordComponentsGet } from './api/search/search';
import { useGetCategoriesApiCategoriesGet } from './api/users/users';
import { useReadPartsOfSpeechApiPartsOfSpeechGet } from './api/parts-of-speech/parts-of-speech';
import { useListSemanticGroupsApiSemanticGroupsGet } from './api/semantic-groups/semantic-groups';
import { useDeleteWordApiWordsWordIdDelete } from './api/words/words';
import { Container, Row, Col, Form, Button, ListGroup, Card, ButtonGroup, Pagination } from 'react-bootstrap';
import styles from './Search.module.css';
import IsAdmin from './IsAdmin';
import { LEVELS } from './constants';

const initialParams = {
    query: '',
    category: '',
    level: '',
    part_of_speech: '',
    component_text: '',
    semantic_group_id: '',
    limit: 20,
    offset: 0,
};

export default function Search() {
    const [params, setParams] = useState(initialParams);
    const [submitted, setSubmitted] = useState(false);
    const [searchType, setSearchType] = useState<'words' | 'phrases' | 'semanticGroups' | 'wordComponents'>('words');
    const [semanticGroupFilters, setSemanticGroupFilters] = useState({ name: '', level: '', frequency: '', category: '', word: '' });
    const [sgParams, setSgParams] = useState({ query: '', category: '', level: '', frequency: '', word: '', limit: 20, offset: 0 });
    const [componentSearchFilters, setComponentSearchFilters] = useState({ text: '', type: '', limit: 20, offset: 0 });
    const [componentSearchSubmitted, setComponentSearchSubmitted] = useState(false);
    const [page, setPage] = useState(0);

    const limit = searchType === 'words' || searchType === 'phrases' ? params.limit : searchType === 'semanticGroups' ? sgParams.limit : componentSearchFilters.limit;
    const offset = page * limit;

    const wordsQuery = useSearchWordsApiSearchWordsGet(
        submitted && searchType === 'words'
            ? {
                ...params,
                category: params.category ? String(params.category) : undefined,
                part_of_speech: params.part_of_speech ? Number(params.part_of_speech) : undefined,
                semantic_group_id: params.semantic_group_id ? Number(params.semantic_group_id) : undefined,
                limit: limit,
                offset: offset,
            }
            : undefined
    );
    const phrasesQuery = useSearchPhrasesApiSearchPhrasesGet(
        submitted && searchType === 'phrases'
            ? {
                ...params,
                category: params.category ? String(params.category) : undefined,
                semantic_group_id: params.semantic_group_id ? Number(params.semantic_group_id) : undefined,
                limit: limit,
                offset: offset,
            }
            : undefined
    );
    const sgQuery = useSearchSemanticGroupsApiSearchSemanticGroupsGet(
        submitted && searchType === 'semanticGroups'
            ? {
                ...sgParams,
                query: semanticGroupFilters.name || undefined,
                category: semanticGroupFilters.category || undefined,
                level: semanticGroupFilters.level || undefined,
                frequency: semanticGroupFilters.frequency || undefined,
                word: semanticGroupFilters.word || undefined,
                limit: sgParams.limit,
                offset: sgParams.offset
            }
            : undefined
    );
    const componentQuery = useSearchWordComponentsApiSearchWordComponentsGet(
        componentSearchSubmitted && searchType === 'wordComponents'
            ? {
                query: componentSearchFilters.text || undefined,
                type: componentSearchFilters.type || undefined,
                limit: componentSearchFilters.limit,
                offset: componentSearchFilters.offset ?? 0,
            }
            : undefined
    );

    const isLoading = searchType === 'words' ? wordsQuery.isLoading : searchType === 'phrases' ? phrasesQuery.isLoading : searchType === 'semanticGroups' ? sgQuery.isLoading : componentQuery.isLoading;
    const error = searchType === 'words' ? wordsQuery.error : searchType === 'phrases' ? phrasesQuery.error : searchType === 'semanticGroups' ? sgQuery.error : componentQuery.error;

    const { data: categoriesData, isLoading: categoriesLoading } = useGetCategoriesApiCategoriesGet();
    const { data: partsOfSpeechData, isLoading: posLoading } = useReadPartsOfSpeechApiPartsOfSpeechGet();
    const navigate = useNavigate();

    function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
        const { name, value } = e.target;
        setParams((prev) => ({ ...prev, [name]: value }));
    }

    function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if (searchType === 'wordComponents') {
            setComponentSearchSubmitted(true);
        } else if (searchType === 'semanticGroups') {
            setSubmitted(true);
        } else {
            setSubmitted(true);
        }
        setPage(0);
    }

    function handleLimitChange(e: React.ChangeEvent<any>) {
        const { value } = e.target;
        if (searchType === 'words' || searchType === 'phrases') {
            setParams(prev => ({ ...prev, limit: Number(value) }));
            setPage(0);
        } else if (searchType === 'semanticGroups') {
            setSgParams(prev => ({ ...prev, limit: Number(value) }));
            setPage(0);
        } else if (searchType === 'wordComponents') {
            setComponentSearchFilters(prev => ({ ...prev, limit: Number(value) }));
            setPage(0);
        }
    }

    function handleMainSearchChange(e: React.ChangeEvent<HTMLInputElement>) {
        const { value } = e.target;
        if (searchType === 'words' || searchType === 'phrases') {
            setParams(prev => ({ ...prev, query: value }));
        } else if (searchType === 'semanticGroups') {
            setSemanticGroupFilters(prev => ({ ...prev, name: value }));
        } else if (searchType === 'wordComponents') {
            setComponentSearchFilters(prev => ({ ...prev, text: value }));
        }
    }

    const totalCount =
        searchType === 'words' && wordsQuery.data?.data?.total_count ? wordsQuery.data.data.total_count :
        searchType === 'phrases' && phrasesQuery.data?.data?.total_count ? phrasesQuery.data.data.total_count :
        searchType === 'semanticGroups' && sgQuery.data?.data?.total_count ? sgQuery.data.data.total_count :
        searchType === 'wordComponents' && componentQuery.data?.data?.total_count ? componentQuery.data.data.total_count :
        0;
    const totalPages = Math.ceil(totalCount / limit);

    return (
        <div className={styles.searchPage}>
            <div className={styles.filtersPanel}>
                <h3>Фільтри</h3>
                {searchType === 'words' && (
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Категорія</Form.Label>
                            <Form.Select name="category" value={params.category} onChange={handleChange} disabled={categoriesLoading}>
                                <option value="">Будь-яка категорія</option>
                        {categoriesData && categoriesData.data && categoriesData.data.map((cat: any) => (
                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Рівень</Form.Label>
                            <Form.Select name="level" value={params.level} onChange={handleChange}>
                                <option value="">Будь-який рівень</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Частина мови</Form.Label>
                            <Form.Select name="part_of_speech" value={params.part_of_speech} onChange={handleChange} disabled={posLoading}>
                                <option value="">Будь-яка частина мови</option>
                        {partsOfSpeechData && partsOfSpeechData.data && partsOfSpeechData.data.map((pos: any) => (
                            <option key={pos.id} value={pos.id}>{pos.name}</option>
                        ))}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Показувати по</Form.Label>
                            <Form.Control name="limit" type="number" value={limit} onChange={handleLimitChange} min={1} max={100} />
                        </Form.Group>
                    </Form>
                )}
                {searchType === 'phrases' && (
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Категорія</Form.Label>
                            <Form.Select name="category" value={params.category} onChange={handleChange} disabled={categoriesLoading}>
                                <option value="">Будь-яка категорія</option>
                                {categoriesData && categoriesData.data && categoriesData.data.map((cat: any) => (
                                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Рівень</Form.Label>
                            <Form.Select name="level" value={params.level} onChange={handleChange}>
                                <option value="">Будь-який рівень</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Показувати по</Form.Label>
                            <Form.Control name="limit" type="number" value={limit} onChange={handleLimitChange} min={1} max={100} />
                        </Form.Group>
                    </Form>
            )}
            {searchType === 'semanticGroups' && (
                    <Form onSubmit={e => e.preventDefault()}>
                        <Form.Group className="mb-3">
                            <Form.Label>Назва</Form.Label>
                            <Form.Control name="name" value={semanticGroupFilters.name} onChange={e => setSemanticGroupFilters(f => ({ ...f, name: e.target.value }))} />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Рівень</Form.Label>
                            <Form.Select name="level" value={semanticGroupFilters.level} onChange={e => setSemanticGroupFilters(f => ({ ...f, level: e.target.value }))}>
                                <option value="">Будь-який рівень</option>
                                {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Категорія</Form.Label>
                            <Form.Select name="category" value={semanticGroupFilters.category} onChange={e => setSemanticGroupFilters(f => ({ ...f, category: e.target.value }))} disabled={categoriesLoading}>
                                <option value="">Будь-яка категорія</option>
                        {categoriesData && categoriesData.data && categoriesData.data.map((cat: any) => (
                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Слово</Form.Label>
                            <Form.Control name="word" value={semanticGroupFilters.word} onChange={e => setSemanticGroupFilters(f => ({ ...f, word: e.target.value }))} />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Показувати по</Form.Label>
                            <Form.Control name="limit" type="number" value={sgParams.limit} onChange={e => setSgParams(f => ({ ...f, limit: Number(e.target.value) }))} />
                        </Form.Group>
                    </Form>
            )}
            {searchType === 'wordComponents' && (
                    <Form onSubmit={e => e.preventDefault()}>
                        <Form.Group className="mb-3">
                            <Form.Label>Текст компонента</Form.Label>
                            <Form.Control name="text" value={componentSearchFilters.text} onChange={e => setComponentSearchFilters(f => ({ ...f, text: e.target.value }))} />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Тип</Form.Label>
                            <Form.Select name="type" value={componentSearchFilters.type} onChange={e => setComponentSearchFilters(f => ({ ...f, type: e.target.value }))}>
                                <option value="">Будь-який тип</option>
                        <option value="prefix">prefix</option>
                        <option value="root">root</option>
                        <option value="suffix">suffix</option>
                        <option value="infix">infix</option>
                        <option value="postfix">postfix</option>
                        <option value="other">other</option>
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Показувати по</Form.Label>
                            <Form.Control name="limit" type="number" value={componentSearchFilters.limit} onChange={e => setComponentSearchFilters(f => ({ ...f, limit: Number(e.target.value) }))} />
                        </Form.Group>
                    </Form>
                )}
            </div>
            <div className={styles.resultsPanel}>
                <div className={styles.tabs}>
                    <button
                        onClick={() => setSearchType('words')}
                        className={searchType === 'words' ? styles.activeTab : ''}
                    >Слова</button>
                    <button
                        onClick={() => setSearchType('phrases')}
                        className={searchType === 'phrases' ? styles.activeTab : ''}
                    >Фрази</button>
                                        <button
                        onClick={() => setSearchType('semanticGroups')}
                        className={searchType === 'semanticGroups' ? styles.activeTab : ''}
                    >Семантичні групи</button>
                                        <button
                        onClick={() => setSearchType('wordComponents')}
                        className={searchType === 'wordComponents' ? styles.activeTab : ''}
                    >Компоненти слова</button>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
                    <Form className="d-flex" onSubmit={handleSubmit} style={{ width: '100%' }}>
                        <Form.Control
                            type="search"
                            value={searchType === 'words' || searchType === 'phrases' ? params.query : searchType === 'semanticGroups' ? semanticGroupFilters.name : componentSearchFilters.text}
                            onChange={handleMainSearchChange}
                            placeholder="Пошук..."
                            className="me-2"
                        />
                        <Button type="submit" variant="primary">Знайти</Button>
                    </Form>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', background: '#fff', borderRadius: 8, padding: 16, minHeight: 0 }}>
                    {isLoading && <div>Loading...</div>}
                    {error && <div style={{ color: '#d32f2f' }}>Error: {error.message}</div>}

                    {searchType === 'words' && submitted && wordsQuery.data && (
                        <>
                        <ListGroup>
                            {wordsQuery.data.data?.items?.length > 0 ? (
                                wordsQuery.data.data.items.map((item: any) => (
                                    <ListGroup.Item key={item.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <span style={{ cursor: 'pointer' }} onClick={() => navigate(`/word?id=${item.id}`)}>{item.name || item.text}</span>
                                    </ListGroup.Item>
                                ))
                            ) : (
                                <ListGroup.Item>Не знайдено слів.</ListGroup.Item>
                            )}
                        </ListGroup>
                        {totalPages > 1 && (
                            <Pagination className="mt-3">
                                <Pagination.First onClick={() => setPage(0)} disabled={page === 0} />
                                <Pagination.Prev onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} />
                                {[...Array(totalPages)].map((_, idx) => (
                                    <Pagination.Item key={idx} active={idx === page} onClick={() => setPage(idx)}>
                                        {idx + 1}
                                    </Pagination.Item>
                                ))}
                                <Pagination.Next onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1} />
                                <Pagination.Last onClick={() => setPage(totalPages - 1)} disabled={page === totalPages - 1} />
                            </Pagination>
                        )}
                        </>
                    )}

                    {searchType === 'phrases' && submitted && phrasesQuery.data && (
                        <>
                        <ListGroup>
                            {phrasesQuery.data.data?.items?.length > 0 ? (
                                phrasesQuery.data.data.items.map((item: any) => (
                                    <ListGroup.Item key={item.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <span style={{ cursor: 'pointer' }} onClick={() => navigate(`/phrase?id=${item.id}`)}>
                                            {item.text || item.name || (Array.isArray(item.words) && item.words.length > 0 ? item.words.map((w: any) => w.text).join(' ') : 'Без назви')}
                                        </span>
                                    </ListGroup.Item>
                            ))
                        ) : (
                                <ListGroup.Item>Не знайдено фраз.</ListGroup.Item>
                        )}
                        </ListGroup>
                        {totalPages > 1 && (
                            <Pagination className="mt-3">
                                <Pagination.First onClick={() => setPage(0)} disabled={page === 0} />
                                <Pagination.Prev onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} />
                                {[...Array(totalPages)].map((_, idx) => (
                                    <Pagination.Item key={idx} active={idx === page} onClick={() => setPage(idx)}>
                                        {idx + 1}
                                    </Pagination.Item>
                                ))}
                                <Pagination.Next onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1} />
                                <Pagination.Last onClick={() => setPage(totalPages - 1)} disabled={page === totalPages - 1} />
                            </Pagination>
                        )}
                        </>
                    )}

                    {searchType === 'semanticGroups' && submitted && sgQuery.data && (
                        <>
                        <ListGroup>
                            {sgQuery.data.data?.items?.length > 0 ? (
                                sgQuery.data.data.items.map((item: any) => (
                                    <ListGroup.Item key={item.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <span style={{ cursor: 'pointer' }} onClick={() => navigate(`/semantic-group?id=${item.id}`)}>{item.name}</span>
                                    </ListGroup.Item>
                                ))
                            ) : (
                                <ListGroup.Item>Не знайдено семантичних груп.</ListGroup.Item>
                            )}
                        </ListGroup>
                        {totalPages > 1 && (
                            <Pagination className="mt-3">
                                <Pagination.First onClick={() => setPage(0)} disabled={page === 0} />
                                <Pagination.Prev onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} />
                                {[...Array(totalPages)].map((_, idx) => (
                                    <Pagination.Item key={idx} active={idx === page} onClick={() => setPage(idx)}>
                                        {idx + 1}
                                    </Pagination.Item>
                                ))}
                                <Pagination.Next onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1} />
                                <Pagination.Last onClick={() => setPage(totalPages - 1)} disabled={page === totalPages - 1} />
                            </Pagination>
                        )}
                        </>
                    )}

                    {searchType === 'wordComponents' && componentSearchSubmitted && componentQuery.data && (
                        <>
                        <ListGroup>
                            {componentQuery.data.data?.items?.length > 0 ? (
                                componentQuery.data.data.items.map((comp: any) => (
                                    <ListGroup.Item key={comp.id}>
                                        <div><strong>Тип:</strong> {comp.type}</div>
                                        <div><strong>Текст:</strong> <span style={{ cursor: 'pointer', color: '#1976d2', textDecoration: 'underline' }} onClick={() => navigate(`/component?id=${comp.id}`)}>{comp.text}</span></div>
                                        <div><strong>Значення:</strong> {comp.meanings?.map((m: any) => m.meaning).join(', ')}</div>
                                        <div><strong>Кількість значень:</strong> {comp.value_count}</div>
                                    </ListGroup.Item>
                                ))
                            ) : (
                                <ListGroup.Item>Не знайдено компонентів.</ListGroup.Item>
                            )}
                        </ListGroup>
                        {totalPages > 1 && (
                            <Pagination className="mt-3">
                                <Pagination.First onClick={() => setPage(0)} disabled={page === 0} />
                                <Pagination.Prev onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} />
                                {[...Array(totalPages)].map((_, idx) => (
                                    <Pagination.Item key={idx} active={idx === page} onClick={() => setPage(idx)}>
                                        {idx + 1}
                                    </Pagination.Item>
                                ))}
                                <Pagination.Next onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1} />
                                <Pagination.Last onClick={() => setPage(totalPages - 1)} disabled={page === totalPages - 1} />
                            </Pagination>
                        )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
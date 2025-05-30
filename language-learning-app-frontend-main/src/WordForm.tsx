import { useState } from 'react';
import { useCreateWordApiWordsPost, useUpdateWordApiWordsWordIdPut } from './api/words/words';
import { GENDERS, CASES, LEVELS } from './constants';
import { useReadPartsOfSpeechApiPartsOfSpeechGet } from './api/parts-of-speech/parts-of-speech';
import styles from './WordForm.module.css';
import type { WordResponse } from './api/model';
import { useGetCategoriesApiCategoriesGet } from './api/categories/categories';
import Select from 'react-select';
import type { MultiValue } from 'react-select';

interface WordFormProps {
    onSuccess?: () => void;
    word?: WordResponse;
}

export default function WordForm({ onSuccess, word }: WordFormProps) {
    const [text, setText] = useState(word?.text || '');
    const [wordCase, setWordCase] = useState(word?.case || 'Nominativ');
    const [reflexivity, setReflexivity] = useState(word?.reflexivity || false);
    const [partOfSpeech, setPartOfSpeech] = useState(word?.part_of_speech ? word.part_of_speech : 0);
    const [gender, setGender] = useState(word?.gender || '');
    const [pluralForm, setPluralForm] = useState(word?.plural_form || '');
    const [verbForm2, setVerbForm2] = useState(word?.verb_form2 || '');
    const [verbForm3, setVerbForm3] = useState(word?.verb_form3 || '');
    const [level, setLevel] = useState(word?.level || '');
    const [categories, setCategories] = useState<number[]>(word?.categories || []);
    const [createStatus, setCreateStatus] = useState<string | null>(null);
    const createWordMutation = useCreateWordApiWordsPost();
    const updateWordMutation = useUpdateWordApiWordsWordIdPut();
    const { data: partsOfSpeechData } = useReadPartsOfSpeechApiPartsOfSpeechGet();
    const { data: categoriesData } = useGetCategoriesApiCategoriesGet();

    return (
        <form
            className={styles.form}
            onSubmit={e => {
                e.preventDefault();
                setCreateStatus(null);
                const payload = {
                    text,
                    case: wordCase,
                    reflexivity,
                    part_of_speech: partOfSpeech ? Number(partOfSpeech) : undefined,
                    gender,
                    plural_form: pluralForm,
                    verb_form2: verbForm2,
                    verb_form3: verbForm3,
                    level,
                    categories,
                };
                if (word) {
                    updateWordMutation.mutate(
                        { wordId: word.id, data: payload },
                        {
                            onSuccess: () => {
                                setCreateStatus('Word updated!');
                                if (onSuccess) onSuccess();
                            },
                            onError: (err: any) => {
                                setCreateStatus('Error: ' + (err?.message || 'Unknown error'));
                            },
                        }
                    );
                } else {
                    createWordMutation.mutate(
                        { data: payload },
                        {
                            onSuccess: () => {
                                setCreateStatus('Word created!');
                                setText('');
                                setWordCase('');
                                setReflexivity(false);
                                setPartOfSpeech(0);
                                setGender('');
                                setPluralForm('');
                                setVerbForm2('');
                                setVerbForm3('');
                                setLevel('');
                                setCategories([]);
                                if (onSuccess) onSuccess();
                            },
                            onError: (err: any) => {
                                setCreateStatus('Error: ' + (err?.message || 'Unknown error'));
                            },
                        }
                    );
                }
            }}
        >
            <div className={styles.row}>
                <span className={styles.label}>Word text</span>
                <input
                    type="text"
                    value={text}
                    onChange={e => setText(e.target.value)}
                    required
                />
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Case</span>
                <select
                    value={wordCase}
                    onChange={e => setWordCase(e.target.value)}
                >
                    {CASES.map(c => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Reflexive</span>
                <label className={styles.checkboxLabel}>
                    <input
                        type="checkbox"
                        checked={reflexivity}
                        onChange={e => setReflexivity(e.target.checked)}
                    />
                </label>
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Part of Speech</span>
                <select
                    value={partOfSpeech}
                    onChange={e => setPartOfSpeech(Number(e.target.value))}
                >
                    {partsOfSpeechData?.data?.sort((poSA, poSB) => poSA.id - poSB.id).map(pos => (
                        <option key={pos.id} value={pos.id}>{pos.name}</option>
                    ))}
                </select>
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Gender</span>
                <select
                    value={gender}
                    onChange={e => setGender(e.target.value)}
                >
                    {GENDERS.map(g => (
                        <option key={g} value={g}>{g}</option>
                    ))}
                </select>
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Plural Form</span>
                <input
                    type="text"
                    value={pluralForm}
                    onChange={e => setPluralForm(e.target.value)}
                />
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Verb Form 2</span>
                <input
                    type="text"
                    value={verbForm2}
                    onChange={e => setVerbForm2(e.target.value)}
                />
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Verb Form 3</span>
                <input
                    type="text"
                    value={verbForm3}
                    onChange={e => setVerbForm3(e.target.value)}
                />
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Level</span>
                <select value={level} onChange={e => setLevel(e.target.value)}>
                    <option value="">—</option>
                    {LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                </select>
            </div>
            <div className={styles.row}>
                <span className={styles.label}>Categories</span>
                <Select
                    isMulti
                    options={categoriesData?.data?.map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                    value={categoriesData?.data?.filter((cat: any) => categories.includes(cat.id)).map((cat: any) => ({ value: cat.id, label: cat.name })) || []}
                    onChange={(selected: MultiValue<{ value: number; label: string }>) => setCategories(selected.map(opt => opt.value))}
                />
            </div>
            <button type="submit" disabled={createWordMutation.isPending || updateWordMutation.isPending}>
                {word ? 'Update Word' : 'Add Word'}
            </button>
            {createStatus && <span>{createStatus}</span>}
        </form>
    );
}

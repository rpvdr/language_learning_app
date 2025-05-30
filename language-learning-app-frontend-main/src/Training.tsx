import React, { useState } from 'react';
import { useStartTrainingApiTrainingStartPost, useSubmitAnswerApiTrainingSubmitAnswerPost, useRateAnswerApiTrainingRateAnswerPost, useSpecialTrainingStartApiSpecialTrainingStartPost } from './api/training/training';
import { useGenerateStudySetApiStudysetGeneratePost } from './api/studyset/studyset';
import styles from './Training.module.css';

interface TrainingQuestion {
    item_type: string;
    item_id: number;
    meanings: { meaning: string; examples: any[] }[];
    part_of_speech?: number;
    part_of_speech_obj?: { id: number; name: string };
}

export default function Training() {
    const [started, setStarted] = useState(false);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [userInput, setUserInput] = useState('');
    const [answerResult, setAnswerResult] = useState<any>(null);
    const [exercises, setExercises] = useState<TrainingQuestion[]>([]);
    const [exerciseType, setExerciseType] = useState<string | null>(null);
    const [exerciseDetail, setExerciseDetail] = useState<TrainingQuestion | null>(null);
    const [selectedRating, setSelectedRating] = useState<number | null>(null);
    const [rootInput, setRootInput] = useState('nehm');
    const [rootError, setRootError] = useState<string | null>(null);
    const [isRootLoading, setIsRootLoading] = useState(false);

    const startTraining = useStartTrainingApiTrainingStartPost();
    const submitAnswer = useSubmitAnswerApiTrainingSubmitAnswerPost();
    const rateAnswer = useRateAnswerApiTrainingRateAnswerPost();
    const generateStudySet = useGenerateStudySetApiStudysetGeneratePost();
    const startSpecialTraining = useSpecialTrainingStartApiSpecialTrainingStartPost();

    const handleStart = (isReview: boolean) => {
        startTraining.mutate({ params: { count: 10, is_review: isReview } }, {
            onSuccess: (res: any) => {
                const questions = res.data?.questions || [];
                setExercises(questions);
                setCurrentIdx(0);
                setStarted(true);
            }
        });
    };

    const handleRootTraining = async () => {
        if (!rootInput.trim()) return;
        setRootError(null);
        setIsRootLoading(true);
        setStarted(false);
        setExercises([]);
        setCurrentIdx(0);
        setUserInput('');
        setAnswerResult(null);
        setExerciseType(null);
        setExerciseDetail(null);
        setSelectedRating(null);
        generateStudySet.mutate({ data: { root: rootInput.trim() } }, {
            onSuccess: () => {
                
                startSpecialTraining.mutate({ params: { count: 10 } }, {
                    onSuccess: (res: any) => {
                        const questions = res.data?.questions || [];
                        setExercises(questions);
                        setCurrentIdx(0);
                        setStarted(true);
                        setIsRootLoading(false);
                    },
                    onError: (err: any) => {
                        setRootError('Не вдалося стартувати тренування.');
                        setIsRootLoading(false);
                    }
                });
            },
            onError: (err: any) => {
                setRootError('Не вдалося згенерувати сет для цього кореня.');
                setIsRootLoading(false);
            }
        });
    };

    React.useEffect(() => {
        if (started && exercises.length > 0 && exercises[currentIdx]) {
            setExerciseType(exercises[currentIdx].item_type);
            setExerciseDetail(exercises[currentIdx]);
        } else {
            setExerciseType(null);
            setExerciseDetail(null);
        }
    }, [started, exercises, currentIdx]);

    const handleCheck = () => {
        if (!exerciseDetail) return;
        submitAnswer.mutate({
            data: {
                item_type: exerciseType || '',
                item_id: exerciseDetail.item_id,
                answer: userInput
            }
        }, {
            onSuccess: (res) => setAnswerResult(res.data)
        });
    };

    const handleNext = () => {
        setUserInput('');
        setAnswerResult(null);
        setCurrentIdx(idx => idx + 1);
        setSelectedRating(null);
    };

    const handleRate = (rating: number) => {
        setSelectedRating(rating);
        if (exerciseDetail && exerciseType) {
            rateAnswer.mutate({
                data: {
                    item_type: exerciseType,
                    item_id: exerciseDetail.item_id,
                    rating: rating,
                    is_review: false
                }
            });
        }
    };

    if (!started) {
        return (
            <div className={styles.root}>
                <button onClick={() => handleStart(false)} disabled={startTraining.isPending}>Вивчення нового</button>
                <button onClick={() => handleStart(true)} disabled={startTraining.isPending}>Повторення</button>
                <div className={styles.rootInputRow}>
                    <input
                        type="text"
                        value={rootInput}
                        onChange={e => setRootInput(e.target.value)}
                        placeholder="Введіть корінь для тренування"
                        disabled={startTraining.isPending || isRootLoading}
                    />
                    <button onClick={handleRootTraining} disabled={startTraining.isPending || startSpecialTraining.isPending || generateStudySet.isPending || !rootInput.trim() || isRootLoading}>
                        Тренування за коренем
                    </button>
                </div>
                {rootError && <div style={{ color: 'red', marginTop: 8 }}>{rootError}</div>}
                {isRootLoading && <div style={{ color: '#888', marginTop: 8 }}>Генерується сет для кореня...</div>}
            </div>
        );
    }
    if (exercises.length === 0) {
        return <div>Завантаження вправ...</div>;
    }
    if (!exerciseDetail) {
        return (
            <div>
                Тренування завершено!
                <button onClick={() => {
                    setStarted(false);
                    setExercises([]);
                    setCurrentIdx(0);
                    setUserInput('');
                    setAnswerResult(null);
                    setExerciseType(null);
                    setExerciseDetail(null);
                    setSelectedRating(null);
                }}>
                    Назад
                </button>
            </div>
        );
    }
    return (
        <div>
            <div>Тип: {exerciseDetail.item_type}</div>
            <div>ID: {exerciseDetail.item_id}</div>
            <div>Значення:</div>
            <ul>
                {exerciseDetail.meanings && exerciseDetail.meanings.map((m: any, i: number) => (
                    <li key={i}>{m.meaning}</li>
                ))}
            </ul>
            <input
                value={userInput}
                onChange={e => setUserInput(e.target.value)}
                disabled={!!answerResult}
                placeholder="Введіть вашу відповідь"
            />
            <button onClick={handleCheck} disabled={submitAnswer.isPending || !!answerResult}>Перевірити</button>
            {answerResult && (
                <div>
                    <div>{answerResult.is_correct ? 'Вірно!' : 'Невірно.'}</div>
                    <div>Правильна відповідь: {answerResult.correct_answer}</div>
                    {answerResult.brief_explanation && <div>Пояснення: {answerResult.brief_explanation}</div>}
                    <div className={styles.ratingBlock}>
                        <div>Як вам ця вправа?</div>
                        <div>
                            <button onClick={() => handleRate(1)} disabled={selectedRating !== null}>Ще раз</button>
                            <button onClick={() => handleRate(2)} disabled={selectedRating !== null}>Важко</button>
                            <button onClick={() => handleRate(3)} disabled={selectedRating !== null}>Добре</button>
                            <button onClick={() => handleRate(4)} disabled={selectedRating !== null}>Легко</button>
                        </div>
                        {selectedRating && <div>Ваша оцінка: {['Ще раз', 'Важко', 'Добре', 'Легко'][selectedRating - 1]}</div>}
                    </div>
                    <button onClick={handleNext}>Далі</button>
                </div>
            )}
        </div>
    );
}

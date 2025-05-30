import styles from './WordChip.module.css';

export type WordChipProps = {
    word: string
    onClick: () => void;
    selected?: boolean;
};

export default function WordChip({ word, onClick }: WordChipProps) {
    return (
        <span
            className={styles.chip}
            onClick={onClick}
        >
            {word}
        </span>
    );
}

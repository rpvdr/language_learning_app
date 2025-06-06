/**
 * Generated by orval v7.9.0 🍺
 * Do not edit manually.
 * German Language Learning API
 * API for managing German words, phrases, components, examples, and semantic groups.
 * OpenAPI spec version: 1.0.0
 */
import type { SemanticGroupDetailResponseCategories } from './semanticGroupDetailResponseCategories';
import type { SemanticGroupDetailResponseCategoryNames } from './semanticGroupDetailResponseCategoryNames';
import type { SemanticGroupDetailResponseLevel } from './semanticGroupDetailResponseLevel';
import type { SemanticGroupDetailResponseFrequency } from './semanticGroupDetailResponseFrequency';
import type { WordResponse } from './wordResponse';
import type { PhraseResponse } from './phraseResponse';

export interface SemanticGroupDetailResponse {
  id: number;
  name: string;
  categories?: SemanticGroupDetailResponseCategories;
  category_names?: SemanticGroupDetailResponseCategoryNames;
  level?: SemanticGroupDetailResponseLevel;
  frequency?: SemanticGroupDetailResponseFrequency;
  word_ids: number[];
  phrase_ids: number[];
  words: WordResponse[];
  phrases: PhraseResponse[];
  member_count: number;
}

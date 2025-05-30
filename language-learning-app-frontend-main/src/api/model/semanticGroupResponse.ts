/**
 * Generated by orval v7.9.0 🍺
 * Do not edit manually.
 * German Language Learning API
 * API for managing German words, phrases, components, examples, and semantic groups.
 * OpenAPI spec version: 1.0.0
 */
import type { SemanticGroupResponseWordIds } from './semanticGroupResponseWordIds';
import type { SemanticGroupResponsePhraseIds } from './semanticGroupResponsePhraseIds';
import type { SemanticGroupResponseCategories } from './semanticGroupResponseCategories';
import type { SemanticGroupResponseCategoryNames } from './semanticGroupResponseCategoryNames';
import type { SemanticGroupResponseLevel } from './semanticGroupResponseLevel';
import type { SemanticGroupResponseFrequency } from './semanticGroupResponseFrequency';
import type { SemanticGroupResponseExplanation } from './semanticGroupResponseExplanation';
import type { SemanticGroupResponseDifferenceExplanation } from './semanticGroupResponseDifferenceExplanation';
import type { WordResponse } from './wordResponse';
import type { PhraseResponse } from './phraseResponse';

export interface SemanticGroupResponse {
  name: string;
  word_ids?: SemanticGroupResponseWordIds;
  phrase_ids?: SemanticGroupResponsePhraseIds;
  categories?: SemanticGroupResponseCategories;
  category_names?: SemanticGroupResponseCategoryNames;
  level?: SemanticGroupResponseLevel;
  frequency?: SemanticGroupResponseFrequency;
  explanation?: SemanticGroupResponseExplanation;
  difference_explanation?: SemanticGroupResponseDifferenceExplanation;
  id: number;
  words?: WordResponse[];
  phrases?: PhraseResponse[];
}

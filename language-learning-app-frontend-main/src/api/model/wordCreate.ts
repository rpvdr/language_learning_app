/**
 * Generated by orval v7.9.0 🍺
 * Do not edit manually.
 * German Language Learning API
 * API for managing German words, phrases, components, examples, and semantic groups.
 * OpenAPI spec version: 1.0.0
 */
import type { WordCreateGender } from './wordCreateGender';
import type { WordCreatePluralForm } from './wordCreatePluralForm';
import type { WordCreateVerbForm2 } from './wordCreateVerbForm2';
import type { WordCreateVerbForm3 } from './wordCreateVerbForm3';
import type { WordCreateReflexivity } from './wordCreateReflexivity';
import type { WordCreateCase } from './wordCreateCase';
import type { WordCreatePartOfSpeech } from './wordCreatePartOfSpeech';
import type { WordCreateCategories } from './wordCreateCategories';

export interface WordCreate {
  text: string;
  gender?: WordCreateGender;
  plural_form?: WordCreatePluralForm;
  verb_form2?: WordCreateVerbForm2;
  verb_form3?: WordCreateVerbForm3;
  reflexivity?: WordCreateReflexivity;
  case: WordCreateCase;
  part_of_speech?: WordCreatePartOfSpeech;
  categories?: WordCreateCategories;
}

export const locales = ['nl', 'en'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'nl';

export const ui = {
  nl: {
    'site.title': 'Schaakstudiespinsels 2',
    'site.subtitle': 'Verzonnen en gesponnen door Ignace Vandecasteele',
    'nav.home': 'Home',
    'nav.chapters': 'Hoofdstukken',
    'nav.studies': 'Studies',
    'study.source': 'Bron',
    'study.moves': 'Zetten',
    'study.variants': 'Varianten',
    'board.start': 'Beginstelling',
    'board.prev': 'Vorige zet',
    'board.next': 'Volgende zet',
    'board.end': 'Eindstelling',
    'lang.switch': 'English',
    'translation.stub': 'Vertaling in voorbereiding.',
  },
  en: {
    'site.title': 'Schaakstudiespinsels 2',
    'site.subtitle': 'Dreamt up and spun together by Ignace Vandecasteele',
    'nav.home': 'Home',
    'nav.chapters': 'Chapters',
    'nav.studies': 'Studies',
    'study.source': 'Source',
    'study.moves': 'Moves',
    'study.variants': 'Variations',
    'board.start': 'Starting position',
    'board.prev': 'Previous move',
    'board.next': 'Next move',
    'board.end': 'Final position',
    'lang.switch': 'Nederlands',
    'translation.stub': 'Translation in progress.',
  },
} as const;

export function t(locale: Locale, key: keyof (typeof ui)['nl']): string {
  return ui[locale][key] ?? ui[defaultLocale][key];
}

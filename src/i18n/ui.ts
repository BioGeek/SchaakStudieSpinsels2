export const locales = ['nl', 'en'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'nl';

export const ui = {
  nl: {
    'site.title': 'SchaakStudieSpinselS 2',
    'site.subtitle': 'Verzonnen en gesponnen door Ignace Vandecasteele',
    'site.tagline': 'Meer dan driehonderd eindspelen',
    'nav.home': 'Home',
    'nav.chapters': 'Hoofdstukken',
    'nav.studies': 'Studies',
    'nav.book': 'Het boek',
    'home.intro':
      'Een interactieve uitgave van Ignace Vandecasteeles eindspelstudies — elke studie als een speelbaar, aanklikbaar bord met de volledige variantenboom.',
    'home.cta': 'Bekijk de studies',
    'home.groups': 'De studies',
    'home.frontmatter': 'Vooraf',
    'home.appendix': 'Verder in het boek',
    'studies.intro': 'De studies, geordend zoals in het boek.',
    'study.source': 'Bron',
    'study.moves': 'Zetten',
    'study.count': 'studies',
    'study.variants': 'Varianten',
    'study.prev': 'Vorige',
    'study.next': 'Volgende',
    'study.allStudies': 'Alle studies',
    'chapter.toStudies': 'Naar de studies',
    'board.start': 'Beginstelling',
    'board.prev': 'Vorige zet',
    'board.next': 'Volgende zet',
    'board.end': 'Eindstelling',
    'lang.switch': 'English',
    'translation.stub': 'Vertaling in voorbereiding.',
  },
  en: {
    'site.title': 'SchaakStudieSpinselS 2',
    'site.subtitle': 'Dreamt up and spun together by Ignace Vandecasteele',
    'site.tagline': 'More than three hundred endgame studies',
    'nav.home': 'Home',
    'nav.chapters': 'Chapters',
    'nav.studies': 'Studies',
    'nav.book': 'The book',
    'home.intro':
      "An interactive edition of Ignace Vandecasteele's endgame studies — each one a playable, clickable board with its full tree of variations.",
    'home.cta': 'Browse the studies',
    'home.groups': 'The studies',
    'home.frontmatter': 'Front matter',
    'home.appendix': 'More in the book',
    'studies.intro': 'The studies, ordered as in the book.',
    'study.source': 'Source',
    'study.moves': 'Moves',
    'study.count': 'studies',
    'study.variants': 'Variations',
    'study.prev': 'Previous',
    'study.next': 'Next',
    'study.allStudies': 'All studies',
    'chapter.toStudies': 'Go to the studies',
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

// The six study chapters ("endgame groups") and the prose page whose content
// is mostly the chapter's epigraph/quote. That quote is rendered inline at the
// head of each group on the studies page rather than living as its own menu
// item — so a chapter is presented together with the studies it introduces.
export const STUDY_CHAPTERS: { number: number; slug: string }[] = [
  { number: 1, slug: 'manke_maljutkas' },
  { number: 2, slug: 'maljutkas' },
  { number: 3, slug: 'mini_studies' },
  { number: 4, slug: 'miniaturen' },
  { number: 5, slug: 'bijna_miniaturen' },
  { number: 6, slug: 'studies' },
];

export const studyChapterSlug = (n: number): string | undefined =>
  STUDY_CHAPTERS.find((c) => c.number === n)?.slug;

// Slugs that are study-chapter intros (folded into the studies page) — kept out
// of the front/back-matter "book" menu.
export const STUDY_CHAPTER_SLUGS = new Set(STUDY_CHAPTERS.map((c) => c.slug));

// The reading-order cut-off between front-matter (preface-type chapters shown
// before the studies) and back-matter (appendices/reviews after them). Used to
// split the "book" menu into two sensible groups.
export const FRONT_MATTER_MAX_ORDER = 5;

// A stable anchor id for a chapter section on the studies page.
export const chapterAnchor = (n: number): string => `groep-${n}`;

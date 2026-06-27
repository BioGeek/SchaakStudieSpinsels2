import { defineCollection, z } from 'astro:content';

const pages = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    order: z.number(),
    translationOf: z.string().optional(),
  }),
});

const studies = defineCollection({
  type: 'data',
  schema: z.object({
    number: z.number(),
    chapter: z.string(),
    chapterNumber: z.number(),
    source: z.string().optional(),
    gbr: z.string(),
    fen: z.string(),
    // Some studies' stipulation glyph doesn't survive text extraction
    // cleanly; allow empty and default to '+'.
    stipulation: z.union([z.enum(['+', '=']), z.literal('')]).default('+'),
    kings: z.string().optional(),
    // Manually curated study: its FEN was corrected via a (gitignored) override
    // sidecar, or its move tree was hand-built because the parser truncates it.
    // Such studies cannot be reproduced by a clean `build_study --all`, so the
    // builder refuses to overwrite them unless `--force` is passed.
    curated: z.boolean().optional(),
    // The starting position has been checked against the Lichess tablebase
    // (7-piece complete + partial 8-piece) and its theoretical value matches the
    // stipulation (a '+' study is a tablebase win for the stronger side, a '='
    // study is a draw). Persisted so the audit isn't re-run and so the UI can
    // show a "tablebase-verified" badge. Absent = not yet verified or >8 pieces.
    tablebaseVerified: z.boolean().optional(),
    moves: z.array(
      z.object({
        id: z.string(),
        ply: z.number(),
        san: z.string(),
        nl: z.string(),
        fenAfter: z.string(),
        variant: z.string().default('main'),
        parent: z.string().nullable().default(null),
      })
    ),
    prose: z.object({
      nl: z.object({
        before: z.string().default(''),
        after: z.string().default(''),
        beforeVariant: z.record(z.string()).default({}),
      }),
      en: z.object({
        before: z.string().default(''),
        after: z.string().default(''),
        beforeVariant: z.record(z.string()).default({}),
      }).optional(),
    }),
  }),
});

export const collections = { pages, studies };

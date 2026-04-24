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
    stipulation: z.enum(['+', '=']),
    kings: z.string().optional(),
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

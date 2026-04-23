import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://schaakstudiespinsels2.be',
  i18n: {
    locales: ['nl', 'en'],
    defaultLocale: 'nl',
    routing: {
      prefixDefaultLocale: true,
      redirectToDefaultLocale: true,
    },
  },
  integrations: [mdx(), tailwind({ applyBaseStyles: false })],
  vite: {
    ssr: {
      // chessground ships as ESM; Astro bundles it cleanly, no extras needed
    },
  },
});

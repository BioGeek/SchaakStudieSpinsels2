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
    server: {
      watch: {
        // The repo also holds the Python pipeline and its caches/data, which
        // the dev server has no reason to watch — watching them exhausts the
        // OS inotify limit (ENOSPC). Ignore everything that isn't site source.
        ignored: [
          '**/.venv/**',
          '**/.mypy_cache/**',
          '**/.pytest_cache/**',
          '**/.ruff_cache/**',
          '**/__pycache__/**',
          '**/data/**',
          '**/.git/**',
          '**/.astro/**',
          '**/dist/**',
        ],
      },
    },
  },
});

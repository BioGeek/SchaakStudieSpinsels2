/** @type {import('tailwindcss').Config} */
import typography from '@tailwindcss/typography';

export default {
  content: ['./src/**/*.{astro,html,md,mdx,ts,tsx,js,jsx}'],
  darkMode: 'media',
  theme: {
    extend: {
      fontFamily: {
        // Cover-inspired small-caps serif for titles; humanist serif for prose
        display: ['"EB Garamond"', 'Georgia', 'serif'],
        serif: ['"EB Garamond"', 'Georgia', 'Cambria', 'serif'],
      },
      colors: {
        paper: {
          light: '#fbf4e6',
          DEFAULT: '#f5ecd7',
          dark: '#221c14',
        },
        ink: {
          DEFAULT: '#1a1a1a',
          soft: '#3b342a',
          muted: '#6a5f4b',
        },
        board: {
          light: '#ead9b3',
          dark: '#8b6b3d',
        },
        accent: {
          DEFAULT: '#7a1f0e',
        },
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': theme('colors.ink.DEFAULT'),
            '--tw-prose-headings': theme('colors.ink.DEFAULT'),
            '--tw-prose-links': theme('colors.accent.DEFAULT'),
            '--tw-prose-quotes': theme('colors.ink.soft'),
            '--tw-prose-counters': theme('colors.ink.muted'),
            '--tw-prose-bullets': theme('colors.ink.muted'),
            maxWidth: '68ch',
            fontFamily: theme('fontFamily.serif').join(', '),
            fontSize: '1.0625rem',
            lineHeight: '1.65',
            '[data-move]': {
              cursor: 'pointer',
              borderRadius: '2px',
              padding: '0 2px',
              transition: 'background-color 120ms',
            },
            '[data-move]:hover': {
              backgroundColor: 'rgba(122, 31, 14, 0.12)',
            },
            '[data-move].active': {
              backgroundColor: 'rgba(122, 31, 14, 0.22)',
              outline: '1px solid rgba(122, 31, 14, 0.45)',
            },
          },
        },
      }),
    },
  },
  plugins: [typography],
};

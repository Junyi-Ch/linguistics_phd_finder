// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Deployed as a GitHub Pages project site:
// https://junyu-jiang0508.github.io/linguistics_phd/
export default defineConfig({
  site: 'https://junyu-jiang0508.github.io',
  base: '/linguistics_phd',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [sitemap()],
});

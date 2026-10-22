// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Deployed as a GitHub Pages project site:
// https://junyi-ch.github.io/linguistics_phd_finder/
export default defineConfig({
  site: 'https://junyi-ch.github.io',
  base: '/linguistics_phd_finder',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [sitemap()],
});

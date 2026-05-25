// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://ekegukeku64-blip.github.io',
  base: '/tech-daily',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  vite: {
    plugins: [tailwindcss()]
  },
  markdown: {
    shikiConfig: {
      theme: 'one-dark-pro',
      wrap: true,
    },
  },
});

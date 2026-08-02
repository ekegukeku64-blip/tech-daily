// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

const site = process.env.SITE_URL?.trim() || 'https://ekegukeku64-blip.github.io';
const requestedBase = process.env.BASE_PATH?.trim() || '/tech-daily';
const base = requestedBase === '/'
  ? '/'
  : `/${requestedBase.replace(/^\/+|\/+$/g, '')}`;

export default defineConfig({
  site,
  base,
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

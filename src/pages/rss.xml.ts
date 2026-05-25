import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';


export async function GET(context: any) {
  const posts = await getCollection('posts');
  const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: '技术日报',
    description: '每日 GitHub 热门 + 技术圈动态',
    site: context.site,
    items: sorted.map(post => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: `${import.meta.env.BASE_URL}${post.id.replace(/\.md$/, '')}/`,
    })),
    customData: '<language>zh-CN</language>',
  });
}

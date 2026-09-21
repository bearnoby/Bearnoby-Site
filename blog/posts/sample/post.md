---
date: 2026-01-01T12:00
title: Sample Post
permalink: sample-post-reference-only
description: A reference post for content writers showing available frontmatter fields, markdown formatting, and how to use images
tags: [reference, formatting]
---

## Frontmatter

Every post's `post.md` needs a frontmatter block at the top:

```
---
date: 2026-09-20T14:30
title: Your Post Title
permalink: your-post-title
description: 
tags: [optional, list, of, tags]
---
```

`date`, `title` , `permalink`, `description` and `tags` are all required fields, and there most be at least one tag.

- `date` must include a full yyyy-MM-ddTHH:mm (e.g. `2026-09-20T23:30`). Posts sort newest-first by this full timestamp
- `title` is the title of the post in both the RSS feed and blog page
- `description` is used in the index and RSS feed as a short description of the post.
- `permalink` sets the public URL

## Markdown formatting

Standard markdown works here: **bold**, *italics*, ~~strikethrough~~, [links](https://bearnoby.com), and lists:
- first item
- second item

```
a fenced code block
```

> a blockquote

## Images

Drop an image file in the same folder as `post.md`, then reference it with a relative
path:

![A chibi bear in a suit](chibi_bear_suit.png)

```markdown
![A chibi bear in a suit](chibi_bear_suit.png)
```

Everything in a post's folder besides `post.md` gets copied as-is into the built page,
so the relative path just works. You can also link a fully external image URL instead
of committing a file, e.g. `![alt](https://example.com/photo.jpg)`.

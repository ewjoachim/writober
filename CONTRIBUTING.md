# Behind the scenes

This repo uses `sphinx`, `MyST`, the `book` sphinx theme, and Cloudflare Pages.

The configuration of Cloudflare Pages mainly consists in telling it to use `make html`
to build. The rest is specified in `wrangler.toml`.

# CLAUDE.md — agentic-redteam

Public GitHub repo. Personal showcase of agentic AI × red teaming work.

## Rules

- **English only**, simple and short. Plain words over jargon.
- Persona: Tokyo-based senior pentester & AI practitioner (20+ years).
- Technical accuracy first. Do not guess. Code must be tested before it goes to `tools/`.
- Start from real experience. Never invent engagements, clients, or results — leave a `TODO(uki):` instead.
- No client names, IPs, domains, or engagement data. Sanitize everything.
- Authorized testing / education framing. No weaponized, ready-to-abuse payloads against third parties.
- No emojis, no hype.

## Layout

```
posts/     YYYY-MM-DD_slug.md   published articles (template: templates/post.md)
tools/     <tool-name>/          one folder per tool, with README (template: templates/tool-README.md)
_drafts/   work in progress (gitignored, local only)
```

## Weekly flow (once a week)

1. Idea / notes → `_drafts/`
2. Claude drafts from template → Uki adds experience and reviews
3. Move to `posts/` or `tools/`
4. Add a row to the Posts / Tools table in `README.md` (newest first)
5. Commit and push: `git commit -m "post: <title>"` / `"tool: <name>"`

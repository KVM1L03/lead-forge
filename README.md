# LeadForge

LeadForge is a local-first lead generation pipeline that turns a natural-language
prompt into qualified leads with drafted outreach emails, ready for human review.
It combines web search (SerpAPI), an LLM qualifier (DSPy + Anthropic), LangGraph
orchestration, Temporal for durability, and a Next.js approval UI — all running
on your machine with no cloud deploy required.

See [CLAUDE.md](./CLAUDE.md) for architecture decisions, coding conventions, and
development workflow.

## Quick start

```bash
cp .env.example .env   # fill in your API keys
make bootstrap
```

## License

Licensed under the PolyForm Noncommercial License 1.0.0.
Free for noncommercial use, study, and modification.
Commercial use requires a separate license — contact klabusit@gmail.com.

© 2026 Kamil Labus

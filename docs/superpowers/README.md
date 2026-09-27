# Experiment and validation plans

This folder holds work plans written with
[Superpowers](https://github.com/obra/superpowers), a Claude Code plugin.

| folder | contents |
|---|---|
| `specs/` | approved designs (`YYYY-MM-DD-<topic>-design.md`) |
| `plans/` | experiment, validation or tooling plans (`YYYY-MM-DD-<topic>.md`) |
| `templates/plan-experimento.md` | template for a new plan |

## Enabling Superpowers

Once per user, inside Claude Code:

```
/plugin install superpowers@claude-plugins-official
```

The `brainstorming` and `writing-plans` skills save into these folders with no
extra configuration.

## Conventions

- One plan per experiment or validation, written before the run.
- When using `writing-plans`, start from `templates/plan-experimento.md`: copy
  its frontmatter to the top of the plan so it shows up on the board.
- Success and failure criteria are fixed before launching.
- When the run ends, update `status`, Result and Conclusion in the same file.
- A discarded plan stays, with the reason.
- Certificates stay in their directories and audits in `audit/`; the plan
  links them under `related` and never copies them.

Frontmatter (same keys in the three MikeSimplex repos):

| key | values |
|---|---|
| `status` | `proposed`, `running`, `done`, `discarded` |
| `type` | `experiment`, `validation`, `tooling` |
| `owner` | `Mike`, `Jaziel`, `ambos` |
| `repo` | repository name |
| `related` | list of paths to logs, results or other plans |

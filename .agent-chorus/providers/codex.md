# Agent Chorus Provider Snippet (codex)

When the user asks cross-agent questions, run Agent Chorus first.

Primary trigger examples:
- "What is Claude doing?"
- "What did Gemini say?"
- "Compare agent outputs"
- "Show the past 3 sessions from Claude"

Intent router:
- "What is Claude doing?" -> `chorus read --agent claude --cwd <project-path> --json`
- "What did Gemini say?" -> `chorus read --agent gemini --cwd <project-path> --json`
- "Compare Codex and Claude outputs" -> `chorus compare --source codex --source claude --cwd <project-path> --json`

Session timing defaults:
- No session ID means latest session in scope.
- "past session" means previous session (exclude latest).
- "past N sessions" means list N+1 and use older N sessions.
- "last N sessions" means list N and include latest session.
- Ask for session ID only after first fetch fails or exact ID is requested.

Commands:
- `chorus read --agent <target-agent> --cwd <project-path> --json`
- `chorus list --agent <agent> --cwd <project-path> --json`
- `chorus search "<query>" --agent <agent> --cwd <project-path> --json`
- `chorus compare --source codex --source gemini --source claude --cwd <project-path> --json`

Use evidence from command output and explicitly report missing session data.

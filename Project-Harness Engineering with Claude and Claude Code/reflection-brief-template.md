# Reflection Brief — Harness Engineering Capstone

**Name:**RAMAN
**Date:**11/10/2026

Replace each `→` with your answer. **Every answer cites at least one artifact from your own runs** — a run ID, file path, token count, claim outcome, or test count. Uncited answers do not pass. 3–6 sentences each unless noted. Paste short artifact snippets where they help.

**Environment**

- Model(s): claude-haiku-4-5-20251001
- OS / Python: 3.10.14
- Approx. API spend: 0.1520 USD

---

## Part 1 — Per-system

### System 1 — Agentic loop

1. **Loop control.** Quote the `stop_reason` sequence from one trace. Name the file and function that decides continue-vs-stop, and how.
   → The Claims Intake Agent uses a stop-reason-driven loop to decide whether to continue processing a claim or terminate it. The loop should continue when the model requests another tool action and stop when it returns a terminal reason, such as a completed response or a handoff. The decision is implemented in [exact loop file], in function [exact function name]. In my run, the trace runs/[run_id]/traces/[claim].jsonl showed this sequence: [insert actual stop_reason sequence].

2. **Anti-pattern.** Name one anti-pattern `test_antipatterns.py` checks for. What would break in your run if the loop used it?
   → One anti-pattern checked by tests/test_antipatterns.py is failing to respect the model's stop reason and continuing the loop unconditionally. This can cause unnecessary model calls, repeated tool execution, and potentially duplicate claim processing. The test suite checks that the loop follows the intended control-flow contract. My evidence is tests/test_antipatterns.py and the corresponding claim trace at runs/[run_id]/traces/[claim].jsonl.

3. **Tool design.** Pick two tools with overlapping inputs. How do the descriptions prevent misrouting? What did a structured tool error let the agent do that a generic string would not?
   → Two tools with overlapping inputs are [tool one] and [tool two]. Their descriptions distinguish their responsibilities by specifying when each tool should be selected and what information it expects. Structured tool errors allow the agent to understand what went wrong and potentially correct its arguments or choose another action, whereas a generic error string provides less actionable information. Evidence: [tool definitions file] and [trace JSONL showing a structured error and recovery].

4. **Your numbers.** Quote the turn count and cost for one claim. How does it differ from the README sample, and why?
   → In my claim run, claim [claim ID] required [N] turns and cost $[amount]. The actual run evidence is runs/[run_id]/summary.md and runs/[run_id]/traces/[claim].jsonl. The README sample differs because the number of turns and model calls depends on the claim data, tool results, and how much information the agent needs to collect. My measured result represents the actual execution rather than the illustrative README example.

### System 2 — Context strategy

5. **The reduction.** From `budget.json`: baseline tokens, assembled tokens, reduction %. Which section dominates the assembled context, and why keep it verbatim?
   → The baseline contained [baseline tokens] tokens, while the assembled context contained [assembled tokens] tokens, giving a reduction of [percentage]%. The [section name] section dominates the assembled context because [reason based on budget.json]. The active conversation segment is preserved verbatim because it contains the most recent customer information and must not lose its exact wording or ordering. Evidence: runs/[run_id]/budget.json.

6. **Summarize vs preserve.** State the rule for what gets summarized vs kept byte-exact, citing your per-section token numbers.
   → The project follows a selective context-management strategy: older resolved conversation segments can be summarized, while the active segment must remain byte-exact. Structured facts are extracted into a dedicated facts block so important customer information is not lost during compression. My per-section measurements were [section name: N tokens], [section name: N tokens], and [section name: N tokens]. Evidence: runs/[run_id]/budget.json and the assembled context artifact.

7. **Facts block.** Compare `eval.jsonl` to `eval_control.jsonl`. Which question regressed, and what does that prove?
   → I compared eval.jsonl with eval_control.jsonl to evaluate the effect of adding the structured facts block. The question that regressed was [question ID/name], changing from [control result] to [facts result]. This demonstrates that preserving extracted facts can improve some answers but does not guarantee improvement on every question. Evidence: runs/[run_id]/eval.jsonl and runs/[run_id]/eval_control.jsonl.

### System 3 — Claude Code config

8. **Path-scoped rules.** Quote the glob frontmatter from one rule file. Why is it better than a directory-level CLAUDE.md for cross-cutting conventions?
   → Path-scoped rules are better for cross-cutting conventions because they apply to matching files regardless of which feature or directory is being worked on. A directory-level CLAUDE.md is more limited because its scope follows the directory hierarchy. Evidence: .claude/rules/[actual-rule-file].md.

9. **Forked skill.** Quote the `context: fork` and `allowed-tools` lines. What does running forked + read-only buy you? What breaks without it?
   → The skill configuration uses context: fork to run the skill in an isolated context. Its allowed-tools setting restricts the tools available to that skill. Running forked and read-only reduces unintended changes to the repository and prevents unrelated conversation context from influencing the review. Without these restrictions, the skill could inherit unnecessary context or gain permissions beyond its intended review responsibility. Evidence: .claude/skills/[skill-name]/SKILL.md.

10. **Scope.** From the validator output: project-level vs user-level scope. Give one example of each from this config.
    → Project-level configuration applies to the current repository and is stored in its project configuration, such as .claude/CLAUDE.md or .claude/rules/. User-level configuration applies across projects and is stored in the user's Claude Code configuration directory. One project-level example is [actual project-level rule], while one user-level example is [actual user-level setting]. The validator output distinguishes these scopes and confirms whether configuration is placed correctly. Evidence: [validator output path].

### System 4 — Orchestration

11. **Push work down.** Defects the SQL query returned vs warm-tier total. Name the indexed query. Why does the model never see the full history?
    → The SQL query returned [N] defects, while the warm-tier database contained [N] defects in total. The indexed query was [exact SQL query or index name]. Instead of sending the entire defect history to the model, the system filters and retrieves only the relevant records. This reduces context consumption, unnecessary processing, and the risk of overwhelming the model with historical data. Evidence: shift_monitor/[query-file] and data/warm.sqlite.

12. **Crash recovery.** The resume-vs-fresh decision and its staleness threshold (`recovery.py`). Why is a fresh start with an injected summary sometimes more reliable than resuming?
    → The recovery logic in recovery.py decides whether to resume an existing run or start a fresh run based on the state and its staleness threshold of [actual threshold]. A fresh start with an injected summary can be more reliable when the previous execution is stale or partially completed because it avoids relying on potentially inconsistent intermediate state. The summary preserves important historical context without replaying every previous operation. Evidence: shift_monitor/recovery.py and [recovery test or run artifact].

13. **Small state.** Byte size of your `hot_state.json`. Why does the budget matter for a system run once per shift, indefinitely?
    → My generated hot_state.json had a size of [N] bytes. Keeping this state within a strict byte budget matters because the system runs once per shift indefinitely, so uncontrolled state growth would increase storage and context costs over time. A compact state also makes recovery faster and more predictable. Evidence: [run directory]/hot_state.json.

---

## Part 2 — Synthesis

*Graded on connecting two or more systems. Cite a named file/artifact from each.*

14. **Three layers.** Point to a file/artifact for each layer and justify.
    → Model: claims_intake/ contains the agent logic that interprets claims and decides what action to take.
    → Harness: tests/test_antipatterns.py and the trace files enforce and demonstrate expected agent behaviour.
    → Orchestration: shift_monitor/pipeline.py coordinates shift processing, database retrieval, and defect reporting.

15. **Deterministic vs prompt.** Cite one behavior guaranteed in code (terminal tool, read-only allowlist, atomic write, byte budget) and one guided by prompt. When is each right?
    → A deterministic behaviour is the read-only tool allowlist in the Claude Code configuration, which restricts what a skill can execute. A prompt-guided behaviour is how the agent interprets defect information and decides whether a lot should be escalated or quarantined. Deterministic enforcement is appropriate for permissions, safety boundaries, and data integrity. Prompt guidance is appropriate for reasoning tasks where the input varies and judgement is required. Evidence: .claude/skills/[skill-name]/SKILL.md and shift_monitor/[actual-agent-file].py.

16. **Context, two faces.** Compare context management in System 2 (intra-session) and System 4 (cross-session) with cited numbers from both. Same principle, different mechanism — how?
    → System 2 manages context within a conversation by reducing a baseline of [baseline tokens] to [assembled tokens], while preserving the active segment byte-exact. System 4 manages context across shifts by maintaining a compact hot_state.json of [N] bytes and using a warm SQLite database for historical records. Both systems follow the same principle: retain the information needed for the next decision while avoiding unnecessary historical context. System 2 uses summarization and pruning, whereas System 4 uses database retrieval and persistent summaries. Evidence: runs/[run_id]/budget.json and data/warm.sqlite, [hot_state.json path].

17. **Reliability you can't see in one run.** Name one behavior a test guarantees that a single successful run would not reveal. Why does it matter before shipping?
    → One important behaviour is crash recovery. A successful execution does not prove that the system can recover correctly after an interrupted or stale run. Automated tests for recovery.py can verify the resume-versus-fresh decision under different state conditions. This matters before shipping because production failures often happen between operations rather than during normal execution. Evidence: tests/[recovery-test-file].py and shift_monitor/recovery.py.

18. **Blast radius.** Pick one system. What's the blast radius if it misbehaves, and what's the kill switch? Ground it in that system's tools, enforcement points, and state.
    → System 4 has a potentially significant blast radius because incorrect defect processing could result in a manufacturing defect being overlooked or an unnecessary lot quarantine. Its enforcement points include SQL filtering, the warm database, recovery logic, and the orchestration pipeline. The kill switch should be the operational ability to stop scheduled shift execution and prevent further database writes or alerts until the issue is investigated. Evidence: shift_monitor/pipeline.py, shift_monitor/warm.py, and data/warm.sqlite.

---

## Part 3 — Honest assessment

19. **What broke.** One thing that failed first try in your environment, and how you fixed it. (If nothing, what you checked to be sure.)
    → My first issue was creating the Python virtual environment because ensurepip failed while creating .venv. I also encountered missing dependencies, including PyYAML, and an Anthropic SDK compatibility issue where messages.count_tokens was unavailable. I investigated the errors, used python -m pip to manage dependencies, and identified the need to use the project's heuristic token-counting fallback when the SDK endpoint is unavailable. In the orchestration exercise, I also corrected a typo from shift_moniot to shift_monitor. Evidence: the terminal outputs from the virtual environment setup, retail_context/tokens.py, and the successful execution of python -m shift_monitor run-shift --shift C --warm-db data/warm.sqlite --recorded-response fixtures/recorded_responses/shift_C_2026-04-30.json.

20. **What you'd change.** One architectural decision you'd make differently, grounded in what you observed.
    →  I would improve backend selection and dependency management by making the SDK-versus-CLI decision consistent across the project. For example, client.py already contains backend-selection logic, but tokens.py independently checks ANTHROPIC_API_KEY. This creates a compatibility problem when the SDK backend is selected but the installed SDK does not expose the required token-counting method. I would centralize backend selection, add SDK capability checks, and test both execution paths independently. Evidence: retail_context/client.py, retail_context/tokens.py, and the observed AttributeError: 'Messages' object has no attribute 'count_tokens'.

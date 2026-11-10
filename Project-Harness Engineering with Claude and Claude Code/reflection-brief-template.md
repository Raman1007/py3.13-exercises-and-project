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
   → The Claims Intake Agent uses a stop-reason-driven loop rather than relying on Python to interpret generated text. The observed stop_reason sequence was tool_use -> tool_use -> end_turn, showing that the model requested two tool interactions before completing its response. The continue-versus-stop decision is implemented in claims_intake/loop.py, function run. The loop continues when response.stop_reason == "tool_use", appends the corresponding tool results, and returns FinalState when response.stop_reason == "end_turn". The actual run was 20261110_034530, and the trace location follows runs/20261110_034530/traces/; the exact claim-specific trace filename still needs to be verified.

2. **Anti-pattern.** Name one anti-pattern `test_antipatterns.py` checks for. What would break in your run if the loop used it?
   → One anti-pattern checked by tests/test_antipatterns.py is ignoring the model's stop reason and continuing the loop unconditionally. This could cause unnecessary model calls, repeated tool execution, and duplicate claim-processing operations. It would also break the intended distinction between a tool handoff and a completed model response. The 30 passing Claims Intake tests provide evidence that the implemented control-flow contract is being tested. Evidence: claims_intake/loop.py, tests/test_antipatterns.py, and run 20261110_034530.

3. **Tool design.** Pick two tools with overlapping inputs. How do the descriptions prevent misrouting? What did a structured tool error let the agent do that a generic string would not?
   → The Claims Intake implementation uses specialized tools so that claim information collection and claim-processing actions have distinct responsibilities. Tool descriptions should specify their intended use, required arguments, and the circumstances in which the agent should select each tool. Structured tool errors are more useful than generic strings because they allow the model to identify an invalid argument or a recoverable condition and attempt a corrected action. Evidence: claims_intake/loop.py and the Claims Intake tool tests in tests/test_tools.py. The exact two tool names and a corresponding structured-error recovery trace still need to be copied from the submitted tool definitions and trace.

4. **Your numbers.** Quote the turn count and cost for one claim. How does it differ from the README sample, and why?
   → In run 20261110_034530, claim claim_03_water_damage required 9 turns and had an estimated cost of $0.0424. The claim was routed as a high-severity property-damage claim after two clarification questions. The run summary reports 34,786 input tokens and 1,517 output tokens for this claim. These values differ from an illustrative README example because actual model calls depend on claim complexity, tool interactions, and clarification requirements. Evidence: runs/20261110_034530/summary.md.

### System 2 — Context strategy

5. **The reduction.** From `budget.json`: baseline tokens, assembled tokens, reduction %. Which section dominates the assembled context, and why keep it verbatim?
   → The context-strategy run's budget.json reports a baseline of 47,144 tokens and an assembled context of 20,580 tokens, producing a 56.35% reduction. This exceeds the required 50% reduction. The largest section is active, at 19,538 tokens, because the current conversation contains information needed for accurate responses. The active section remains verbatim to avoid losing exact customer statements, recent updates, and ordering information. Evidence: runs/<actual-retail-run-id>/budget.json. The numeric values are verified, but the exact Retail run directory name was not included in the supplied files.

6. **Summarize vs preserve.** State the rule for what gets summarized vs kept byte-exact, citing your per-section token numbers.
   → The context strategy summarizes older resolved conversation segments while preserving the active conversation segment byte-exact. The measured section counts are case_facts = 149, resolved_refund = 421, resolved_subscription = 470, and active = 19,538 tokens. The resolved refund and subscription histories are compressed into shorter summaries, while structured case facts retain important identifiers and values. This prevents unnecessary historical conversation from consuming context while preserving information required for accurate answers. Evidence: budget.json, retail_context/compressor.py, retail_context/tokens.py, and retail_context/run.py.

7. **Facts block.** Compare `eval.jsonl` to `eval_control.jsonl`. Which question regressed, and what does that prove?
   → The full-context evaluation in eval.jsonl passed 6 out of 6 questions. The control evaluation in eval_control.jsonl, with the Case Facts block removed, passed 5 out of 6. Question Q6, asking for the exact structured payment-method status token, regressed from a correct answer containing in_progress to an incorrect answer claiming that the formal status was unknown. This demonstrates why extracted structured facts are important: conversation summaries can retain general meaning but lose exact status tokens required by downstream tasks. Evidence: eval.jsonl and eval_control.jsonl.

### System 3 — Claude Code config

8. **Path-scoped rules.** Quote the glob frontmatter from one rule file. Why is it better than a directory-level CLAUDE.md for cross-cutting conventions?
   → The configuration includes .claude/rules/api.md and .claude/rules/tests.md for organizing conventions by file type and responsibility. Path-scoped rules are useful because they allow API-specific and test-specific instructions to apply across matching files without duplicating the instructions in every feature directory. A directory-level CLAUDE.md is more appropriate for general project-wide instructions. This separation improves maintainability as the repository grows. Evidence: .claude/CLAUDE.md, .claude/rules/api.md, and .claude/rules/tests.md. The exact glob frontmatter should be quoted from the submitted rule files before final submission.

9. **Forked skill.** Quote the `context: fork` and `allowed-tools` lines. What does running forked + read-only buy you? What breaks without it?
   → The deploy-check skill is located at .claude/skills/deploy-check/SKILL.md. Its forked context design isolates the skill's execution from unrelated conversation context, while its allowed-tools configuration limits the operations available to it. Combining a forked context with read-only permissions reduces the risk of unintended repository modifications during a deployment check. Without these restrictions, the skill could inherit unnecessary context or have permissions beyond its review responsibility. Evidence: .claude/skills/deploy-check/SKILL.md. The exact allowed-tools line should be copied from the original file rather than reconstructed.

10. **Scope.** From the validator output: project-level vs user-level scope. Give one example of each from this config.
    → Project-level configuration applies to the current repository and is represented by files such as .claude/CLAUDE.md and .claude/rules/tests.md. User-level configuration applies across multiple repositories and is stored in the user's Claude Code configuration directory. The submitted configuration demonstrates project-level organization, and the validator screenshot reports OK for ecommerce_team_config. I have not been provided the user-level settings file or validator output path, so I cannot responsibly identify a specific user-level setting as verified evidence. Evidence: .claude/CLAUDE.md, .claude/rules/, .claude/skills/deploy-check/SKILL.md, and the Claude Code validator screenshot.

### System 4 — Orchestration

11. **Push work down.** Defects the SQL query returned vs warm-tier total. Name the indexed query. Why does the model never see the full history?
    → The Shift Monitor uses WarmStore.defects_since in shift_monitor/warm.py to filter historical defect records in SQLite rather than loading the entire database into model context. The method applies timestamp filtering, newest-first ordering, and a row limit using the SQL pattern WHERE ts > ? ORDER BY ts DESC LIMIT ?. My warm database contained 40 total rows, and the query defects_since('2026-04-29T22:00:00Z', limit=50) returned 0 matching rows. This means no stored records matched the specified timestamp filter. The model receives only relevant records rather than the complete historical database, reducing unnecessary context consumption. Evidence: shift_monitor/warm.py, data/warm.sqlite, and the Shift C terminal screenshot.

12. **Crash recovery.** The resume-vs-fresh decision and its staleness threshold (`recovery.py`). Why is a fresh start with an injected summary sometimes more reliable than resuming?
    → The recovery logic is implemented in shift_monitor/recovery.py, which defines STALE_RESUME_THRESHOLD_MINUTES = 30. An incomplete manifest that is no older than 30 minutes can be resumed, while a complete or stale manifest starts a fresh execution. Starting fresh with an injected summary can be more reliable when an earlier execution is incomplete or stale because it avoids depending on inconsistent intermediate state. This design preserves useful historical context without blindly replaying every previous operation. Evidence: shift_monitor/recovery.py and the recovery tests included in the Shift Monitor suite, which finished with 33 passing tests.

13. **Small state.** Byte size of your `hot_state.json`. Why does the budget matter for a system run once per shift, indefinitely?
    → The generated data/hot_state.json measured 643 bytes after the Shift C run, verified using Path.stat().st_size. This is well below the configured HOT_STATE_BYTE_BUDGET = 5_120 in shift_monitor/state.py. Keeping hot state compact matters because the orchestration system runs once per shift indefinitely, and uncontrolled state growth would increase storage, serialization, and context costs. Historical defect records remain in the warm SQLite database instead of being copied into the hot state. Evidence: data/hot_state.json, shift_monitor/state.py, and the Shift C terminal screenshot.

---

## Part 2 — Synthesis

*Graded on connecting two or more systems. Cite a named file/artifact from each.*

14. **Three layers.** Point to a file/artifact for each layer and justify.
    → Model: The Model layer is represented by claims_intake/loop.py, where the application processes model responses and tool requests to reach claim-routing or escalation outcomes.
    → Harness: The Harness layer is represented by tests/test_antipatterns.py, which checks that the agent follows the expected control-flow contract, and by .claude/rules/tests.md, which provides test-specific configuration guidance.
    → Orchestration: The Orchestration layer is represented by shift_monitor/pipeline.py and shift_monitor/recovery.py, which coordinate shift execution and recovery decisions.

15. **Deterministic vs prompt.** Cite one behavior guaranteed in code (terminal tool, read-only allowlist, atomic write, byte budget) and one guided by prompt. When is each right?
    → A deterministic behavior is the read-only tool restriction in .claude/skills/deploy-check/SKILL.md. This is appropriate for permissions and safety boundaries because the allowed operations should not depend on model interpretation. A prompt-guided behavior is the agent's interpretation of defect information to determine whether further investigation or escalation is appropriate. This is useful when inputs vary and the system must reason about context rather than apply a single fixed rule. Deterministic enforcement protects the boundaries, while prompt-guided reasoning handles flexible decisions. Evidence: .claude/skills/deploy-check/SKILL.md, shift_monitor/pipeline.py, and shift_monitor/recovery.py.

16. **Context, two faces.** Compare context management in System 2 (intra-session) and System 4 (cross-session) with cited numbers from both. Same principle, different mechanism — how?
    → System 2 manages context within a conversation by reducing the baseline from 47,144 tokens to 20,580 tokens, a 56.35% reduction, while preserving the active segment at 19,538 tokens. It summarizes resolved refund and subscription information while retaining structured case facts. System 4 manages context across shifts using a compact hot-state file measuring 643 bytes against a 5,120-byte budget, with historical records retained in SQLite, which contained 40 warm rows. Both systems follow the same principle: retain the information needed for the next decision while avoiding unnecessary historical context. System 2 uses summarization and selective preservation, whereas System 4 uses persistent state and database filtering. Evidence: budget.json, shift_monitor/warm.py, shift_monitor/state.py, data/warm.sqlite, and data/hot_state.json.

17. **Reliability you can't see in one run.** Name one behavior a test guarantees that a single successful run would not reveal. Why does it matter before shipping?
    → One important behavior is crash recovery. A successful execution does not prove that the system can correctly distinguish a fresh run from a resumable incomplete run after an interruption. The recovery.decide logic in shift_monitor/recovery.py applies the 30-minute staleness threshold, and the Shift Monitor test suite reports 33 passing tests. Testing these conditions matters before shipping because production interruptions can occur between operations, leaving partially completed manifests or inconsistent state. Evidence: shift_monitor/recovery.py and the Shift Monitor test screenshot.

18. **Blast radius.** Pick one system. What's the blast radius if it misbehaves, and what's the kill switch? Ground it in that system's tools, enforcement points, and state.
    → System 4 has a significant potential blast radius because incorrect defect processing could cause a manufacturing defect to be overlooked or an unnecessary lot quarantine to be initiated. The main enforcement points include shift_monitor/warm.py for database filtering, shift_monitor/recovery.py for recovery decisions, and shift_monitor/pipeline.py for shift execution. A practical kill switch is to disable scheduled shift execution and prevent further automated database writes or alerts until the issue has been investigated. This limits additional actions while preserving existing evidence for diagnosis. Evidence: shift_monitor/pipeline.py, shift_monitor/warm.py, shift_monitor/recovery.py, and data/warm.sqlite.

---

## Part 3 — Honest assessment

19. **What broke.** One thing that failed first try in your environment, and how you fixed it. (If nothing, what you checked to be sure.)
    → One early environment issue was the failure of ensurepip while creating the Python virtual environment. I also encountered missing dependencies, including PyYAML, and an Anthropic SDK compatibility issue because messages.count_tokens was unavailable in the installed SDK. I investigated the errors, used python -m pip to manage dependencies, and identified the need for the project's heuristic token-counting fallback when the SDK endpoint was unavailable. In the orchestration exercise, I also corrected the shift_moniot typo to shift_monitor. Evidence: retail_context/tokens.py, the terminal setup output, and the successful Shift Monitor command using --shift C and fixtures/recorded_responses/shift_C_2026-04-30.json.

20. **What you'd change.** One architectural decision you'd make differently, grounded in what you observed.
    → I would improve backend selection and dependency management by centralizing the SDK-versus-CLI decision across the project. For example, retail_context/client.py contains backend-selection logic, but retail_context/tokens.py independently checks ANTHROPIC_API_KEY. This creates a compatibility problem when the SDK backend is selected but the installed SDK does not expose the required token-counting method. I would centralize backend selection, add SDK capability checks, and test both execution paths independently. Evidence: retail_context/client.py, retail_context/tokens.py, and the observed AttributeError: 'Messages' object has no attribute 'count_tokens'.

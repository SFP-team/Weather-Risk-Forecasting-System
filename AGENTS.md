# Project continuity and GitHub handover

## Start every task

Read `HANDOVER.md` first, then the relevant runbook and source files. Inspect Git status and preserve unrelated changes. The handover records evidence, not permission to expand the task.

## Finish every completed request

The user authorizes ongoing GitHub updates for this project after each completed request, including scheduled work that materially advances it.

1. Update `HANDOVER.md` with the verified outcome, changed components, tests actually run, remaining work and blockers. Distinguish implementation from plans and acquisition from scientific validation. Keep it concise and current.
2. Add a dated entry to `docs/PROGRESS_LOG.md` for material progress. Do not duplicate unchanged monitoring results.
3. Review the diff and scan changed files for secrets/private data. Stage explicitly selected project code, tests and documentation only. Never use blanket staging for unknown files.
4. Commit and push to the existing project branch and configured origin. Check remote state first; never force-push, rewrite history or discard other contributors' work. If authentication, network or conflicts block publication, preserve local work and tell the user exactly what remains unpushed.
5. Verify the remote branch points to the resulting commit before saying the work is on GitHub. Report the commit in the final answer. A handover must not claim its own push succeeded before verification.

For read-only requests with no new project facts or changes, do not create empty commits. Report that no repository update was needed. This is an agent workflow, not an independently installed post-prompt hook; other accounts/tools must read these instructions to follow it.

## Publication boundaries

Never commit credentials, authentication files, environment secrets, bulk weather data, raw station archives, personal attachments, or private breeding information. Supervisor transcripts, supplied HTML reports and the original R workflow require a separate publication review before inclusion. Keep downloads on the designated server. Do not include machine-local cache files.

## Weather scope

Follow `DATA_ACQUISITION_HANDOFF.md` and `docs/weather/SERVER_RUNBOOK.md`. Do not restart completed global downloads or duplicate workers. Do not infer authorization for genotype models, paid services, global hourly acquisition or app deployment from the recurring weather task.

---
name: plan-generator
description: For every multi-step task from /Needs_Action, create a structured Plan.md before acting
permissions: filesystem-write, filesystem-read
---

When processing any file in /Needs_Action:

1. Create folder /Plans if it does not exist.
2. Generate unique filename: Plans/PLAN_{original_filename without .md}_{YYYY-MM-DD_HH-MM}.md
3. Write this exact template into the file:

---
created: {current ISO datetime}
source_task: [[{relative path to Needs_Action file}]]
status: in-planning
---

# Task Execution Plan

## Objective
{One clear sentence summarizing the goal from the task file}

## Required Steps
- [ ] Step 1: {first logical action}
- [ ] Step 2: {next action}
- [ ] Step 3: ...
- [ ] Final: Move task file to /Done after completion

## Resources / Tools Needed
- List MCP servers or skills required
- Any human approval points

## Risks
- ...

After writing Plan.md, append link to it in the original Needs_Action file:
[[Plans/{filename}]]

Then continue reasoning with the plan visible.
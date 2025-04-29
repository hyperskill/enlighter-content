---
description: 
globs: 
alwaysApply: true
---
# Educational Course & Stage Authoring Rules

These rules describe **how to build practical educational course** ("project") and its learning steps ("stages").
Follow them whenever you generate or update course content.

---

## 1. Repository Layout

| Item | Pattern | Example |
|------|---------|---------|
| Course directory | `project_<PROJECT_ID>_<project_name_snake>` | `project_42_realtime_chat` |
| Stage file | `<order_num>_<STAGE_ID>_<stage_title_snake>.html` | `3_256_set_up_backend.html` |

1. `<order_num>` starts at **1** and matches the logical learning flow.  
2. mock id with 'ID' if you don't know real ID
3. Use **snake_case** — lower-case and underscores only — for names.

---

## 2. Mandatory File Content Structure (HTML-based Markdown)

Use [markdown.mdc](mdc:.cursor/rules/markdown.mdc) rules to structure content.

---

## 3. Updating Existing courses

1. Respect existing IDs & filenames.  
2. If you **add** or **remove** a stage, adjust the `order_num` sequence and rename files accordingly.  
3. When editing content, keep the HTML wrapper tags intact.

---

## 4. Content structure

1. The entire repository is a collection of independent courses; you are building one such course.
2. The course is broken into 5-15 stages (ideally ≈ 8).
3. Each stage must take ≤ 20 minutes to complete and contain ≤ 400 lines of content.

---

## 5. Methodology

1. Course is practical - the user programs with the help of AI assistant while going through the course
2. Educational course runs inside the development environment (in-IDE learning)
3. Learners complete every task directly in the programming environment.
4. User interracts with programming environment with <callout> blocks. Find more about <callout> markdown in [markdown.mdc](mdc:.cursor/rules/markdown.mdc)
5. <callout> blocks are instructions for AI
6. Embed at least one <callout> block per stage; use additional <callout> blocks whenever helpful.
7. A <callout> block is text the learner will copy-paste to the AI assistant they are coding with.
8. Use <callout> blocks for code generation, environment setup (e.g., creating virtual envs, installing packages), troubleshooting, or asking the assistant clarifying questions.

---

## 6. Education quality

1. Apply best practices in instructional design (clear objectives, incremental difficulty, active recall, feedback loops).
2. Ensure each stage culminates in a tangible coding outcome the learner can run or observe.

---

**Follow these rules strictly** whenever you generate, review, or modify course content.  Consistency ensures every learner enjoys a predictable, high-quality experience inside Cursor IDE.

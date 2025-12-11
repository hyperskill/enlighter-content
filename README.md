# 🌟 Enlighter Content

This repository contains educational content for [Enlighter](https://enlightby.ai) - a platform to learn Vibe Coding.

---

## 📚 Documentation

1. [Content markdown documentation](https://docs.google.com/document/d/1i8C5gUZSSsArFpDyg735-QBMmDlO1lKwxBrUJLq53BM/)
2. Markdown documentation as Cursor's rule in `.cursor/rules/markdown.mdc`
3. Content structure as Cursor's rule in `.cursor/rules/content_builder_instructions.mdc`

---

## 🏗️ Content Structure

Each project follows this structure:

| Item              | Naming Convention | Example |
|-------------------|-------------------|---------|
| Project directory | `project_<PROJECT_ID>_<project_name_snake>` | `project_42_realtime_chat` |
| Stage html file   | `<order_num>_<STAGE_ID>_<stage_title_snake>.html` | `3_256_set_up_backend.html` |

**Key points:**
1. Each project consists of 5-15 sequential learning stages
2. Stages should take ≤20 minutes to complete
3. Each stage should contain ≤400 lines of content
4. More details on content structure can be found in `.cursor/rules/content_builder_instructions.mdc`
5. New projects and stages IDs have to be mocked with `ID`, for example `project_ID_realtime_chat`.

---

## 🖥️ Content Preview

1. **Install Node.js**  
   Download and install from [nodejs.org](https://nodejs.org/) (LTS version recommended)

2. **Install Dependencies**  
   Run this command in the project root:
   ```bash
   npm install
   ```

3. **Start the preview server with:**
   ```bash
   npm start
   ```
4. Open your browser at [http://localhost:3333](http://localhost:3333)
5. Select a project from the dropdown menu
6. Choose a stage within that project
7. The content will load automatically in the preview frame
8. Use "Refresh File List" to update when you add/modify projects or stages

---

## 👩‍💻 How to Contribute

If you want to contribute a project to Enlighter, please follow our [Contributing Guidelines]([CONTRIBUTING.md](https://github.com/hyperskill/enlighter-content/blob/main/CONTRIBUTION.md)).

# 🌟 Enlighter Content Repository

This repository contains educational content for the [Enlighter](https://enlightby.ai) - a platform to learn Vibe Coding.

---

## 📚 Documentation

* [Content markdown documentation](https://docs.google.com/document/d/1i8C5gUZSSsArFpDyg735-QBMmDlO1lKwxBrUJLq53BM/)
* Markdown documentation as Cursor's native rule in `.cursor/rules/markdown.mdc`
* Content structure as Cursor's native rule in `.cursor/rules/content_builder_instructions.mdc`

---

## 🏗️ Content Structure

Each project follows this structure:

| Item              | Naming Convention | Example |
|-------------------|-------------------|---------|
| Project directory | `project_<PROJECT_ID>_<project_name_snake>` | `project_42_realtime_chat` |
| Stage html file   | `<order_num>_<STAGE_ID>_<stage_title_snake>.html` | `3_256_set_up_backend.html` |

**Key points:**
* Each project consists of 5-15 sequential learning stages
* Stages should take ≤20 minutes to complete
* Each stage should contain ≤400 lines of content
* More details on content structure can be found in `.cursor/rules/content_builder_instructions.mdc`
* New projects and stages IDs have to be mocked with `ID`, for example `project_ID_realtime_chat` 

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

**Viewing Your Content:**
1. Open your browser on [http://localhost:3333](http://localhost:3333)
2. Select a project from the dropdown menu
3. Choose a stage within that project
4. The content will load automatically in the preview iframe
5. Use "Refresh File List" to update when you add/modify projects or stages

---

## 👩‍💻 How to Contribute

1. **Follow Structure Guidelines**  
   Create content according to the markdown rules and project structure.
   Use `<callout>` blocks for AI assistant interactions

3. **Test Your Content**  
   Verify formatting and functionality using the preview server

4. **Keep Content Focused**  
   Ensure each project is concise and accomplishes a specific learning goal

5. **Specify metadata**

   For projects:
   - Project name
   - Project description (2-3 sentences)
   - Short description (1 sentence)
   - Categories. For example: `Cursor IDE, Vibe Coding, RAG`
   - Target IDE: [Cursor](https://www.cursor.com) or [JetBrain Junie](https://www.jetbrains.com/junie/)
   
   For stages:
   - Stage name

6. **Submit Your Work**  
   Open a pull request with your changes for review. Write down metadata from previous step to PR's description.

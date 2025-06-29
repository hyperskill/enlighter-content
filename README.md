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

### 📋 Project Structure Requirements

1. **Create a project.json file**  
   Each project must include a `project.json` file in the root directory with this schema:
   ```json
   {
     "id": number,
     "title": "string - Project name",
     "description": "string - 2-3 sentences explaining what learners will build",
     "short_description": "string - 1 sentence hook",
     "categories": "string - comma-separated tags (e.g., 'Web, Interactive')",
     "cover_url": "string - URL to project cover image",
     "readme": "string - Full markdown content for the project",
     "ides": "string - target IDE: 'cursor', 'windusrf', or 'junie'"
   }
   ```

2. **Follow Project Stage Structure**  
   Each project should have several stages:
   - **First stage**: Explanatory introduction that explains what we'll learn and build
   - **Middle stages**: Step-by-step implementation phases  
   - **Final stage**: Conclusion with further exploration ideas, next steps, and additional resources

### 🎯 IDE Guidelines & Best Practices

Reference our [cursor rules directory](https://github.com/hyperskill/enlighter-content/tree/main/.cursor/rules) for established content standards and best practices. Cursor IDE users can apply these rules directly, while users of other IDEs should adapt the guidelines to their development environment.


### 📝 Content Guidelines

1. **Write Clear Instructions**  
   Provide step-by-step instructions with explanations of what each step accomplishes.

2. **Keep Content Focused**  
   Each project should accomplish a specific learning goal without unnecessary complexity.

3. **Use Structured Markup**  
   - Follow markdown rules and project structure
   - Use `<callout>` blocks for AI assistant interactions
   - Structure content with proper headings and sections

4. **HTML-Based Lessons**  
   Our interactive lessons are HTML pages that work as plugins in IDEs. Focus on creating engaging, interactive HTML content for learners.

### 🚀 Submission Process

1. **Prepare Your Contribution**  
   - Ensure your `project.json` is complete and follows the schema
   - Test all examples and instructions work as intended
   - Verify formatting using the preview server

2. **Submit Your Work**  
   - Open a pull request with your changes
   - Include project metadata in the PR description
   - Briefly explain what learners will gain from your project

### 🎓 Learning Focus

Structure your contributions to help learners:
- Understand practical AI-assisted development workflows
- Learn through hands-on, interactive HTML-based lessons
- Build real-world projects with step-by-step guidance
- Develop problem-solving skills with AI tools
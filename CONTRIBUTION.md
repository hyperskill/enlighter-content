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
# Supabase Project Instructions

## Project Information
- **Supabase Project ID**: `pdqqywctjlfcaeeaykvj`

## Database Schema Overview
The Supabase project contains the following key tables:

- `users` - User information
- `projects` - Course projects 
- `stages` - Learning stages for each project
- `project_progresses` - Track user progress through projects
- `stage_progresses` - Track user progress through stages

## Instructions for Fetching and Storing Project Stages

### 1. Query stages for a specific project
```sql
SELECT id, title, description, order_num 
FROM stages 
WHERE project_id = <PROJECT_ID> 
ORDER BY order_num ASC;
```

### 2. Create a directory for the project
```
mkdir -p project_<PROJECT_ID>_<PROJECT_NAME>
```

### 3. For each stage, create an HTML file
- File naming: `<stage.order_num>_<stage.id>_<stage.title>.html`
- Convert stage title to underscore case
- Store stage description as HTML content
- HTML content should match exactly content in the database

### 4. Example procedure
```
1. Execute SQL query to fetch all stages for project_id = X
2. Create directory with pattern project_X_project_name
3. For each stage:
   - Format title as underscore_case
   - Create file named {stage.id}_{formatted_title}.html
   - Write stage.description to file
4. Verify all files are created
```

### Execution Example
To fetch and store stages for project_id=38:
1. Query: `SELECT id, title, description, order_num FROM stages WHERE project_id = 38 ORDER BY order_num ASC;`
2. Create directory: `mkdir -p project_38_camera_junie`
3. Create HTML files for each stage with pattern: `1_213_what_you_will_build.html`
4. Write each stage's description HTML to its file 
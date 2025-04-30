import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';
import apiRoutes, { updateHtmlFiles } from './routes.js';
import { ProjectFile } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Server configuration
const app = express();
const PORT = process.env.PORT || 3333;

// Serve static files from the current directory
app.use(express.static(__dirname));

// Allow CORS for development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Use API routes
app.use('/api', apiRoutes);

// Function to extract project and stage info from filename
function extractFileInfo(filePath: string): ProjectFile | null {
  // Extract filename from path
  const fileName = path.basename(filePath);
  
  // Match pattern like: 1_256_set_up_backend.html
  const stageMatch = fileName.match(/^(\d+)_(\d+)_(.+)\.html$/);
  if (stageMatch) {
    const order = parseInt(stageMatch[1], 10);
    const stageId = stageMatch[2];
    const title = stageMatch[3].replace(/_/g, ' ');
    
    // Extract project info from directory path
    const dirName = path.dirname(filePath);
    const projectMatch = path.basename(dirName).match(/^project_(\d+)_(.+)$/);
    
    if (projectMatch) {
      const projectId = projectMatch[1];
      const projectName = projectMatch[2].replace(/_/g, ' ');
      
      return {
        path: filePath,
        project: `${projectId}: ${projectName}`,
        stage: `${stageId}: ${title}`,
        order,
        title
      };
    }
  }
  
  return null;
}

// Scan for HTML files
export async function scanHtmlFiles() {
  try {
    const files = await glob('project_*/**/*.html', { ignore: 'node_modules/**' });
    
    const projectFiles = files
      .map(file => extractFileInfo(file))
      .filter((file): file is ProjectFile => file !== null)
      .sort((a, b) => {
        // First sort by project
        if (a.project !== b.project) {
          return a.project.localeCompare(b.project);
        }
        // Then by order
        return a.order - b.order;
      });
      
    // Update the shared file list
    updateHtmlFiles(projectFiles);
    
    console.log(`Found ${projectFiles.length} HTML files`);
    return projectFiles;
  } catch (error) {
    console.error('Error scanning HTML files:', error);
    return [];
  }
}

// Serve index.html for all routes (SPA handling)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Initial scan of HTML files
async function startServer() {
  // Perform initial scan
  await scanHtmlFiles();
  
  app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
  });
}

startServer(); 
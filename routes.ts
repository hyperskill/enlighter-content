import express from 'express';
import fs from 'fs/promises';
import { ProjectFile } from './types.js';
import { scanHtmlFiles } from './server.js';

const router = express.Router();

// Store for HTML files
let htmlFiles: ProjectFile[] = [];

// Update the HTML files list
export const updateHtmlFiles = (files: ProjectFile[]) => {
  htmlFiles = files;
};

// API endpoint to get all HTML files
router.get('/files', async (req, res) => {
  try {
    // Scan for files on demand
    const projectFiles = await scanHtmlFiles();
    
    // Group files by project
    const projectsMap = new Map<string, ProjectFile[]>();
    
    projectFiles.forEach(file => {
      if (!projectsMap.has(file.project)) {
        projectsMap.set(file.project, []);
      }
      projectsMap.get(file.project)!.push(file);
    });
    
    // Convert to array
    const projects = Array.from(projectsMap.entries()).map(([project, files]) => ({
      name: project,
      stages: files.sort((a, b) => a.order - b.order)
    }));
    
    res.json(projects);
  } catch (error) {
    console.error('Error processing files:', error);
    res.status(500).json({ error: 'Failed to scan files' });
  }
});

// Get specific file info
router.get('/file/:path', async (req, res) => {
  try {
    // Scan for files on demand to ensure up-to-date info
    const projectFiles = await scanHtmlFiles();
    
    const filePath = decodeURIComponent(req.params.path);
    const file = projectFiles.find(f => f.path === filePath);
    
    if (file) {
      res.json(file);
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Error processing file request:', error);
    res.status(500).json({ error: 'Failed to scan files' });
  }
});

// Get HTML content for a specific file
router.get('/content', async (req, res) => {
  try {
    const filePath = req.query.path as string;
    
    if (!filePath) {
      return res.status(400).json({ error: 'File path is required' });
    }
    
    try {
      // Read the file content
      const content = await fs.readFile(filePath, 'utf-8');
      res.send(content);
    } catch (error) {
      console.error(`Error reading file ${filePath}:`, error);
      res.status(404).json({ error: 'File not found or could not be read' });
    }
  } catch (error) {
    console.error('Error processing content request:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router; 
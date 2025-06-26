import { DOMParser } from '@xmldom/xmldom';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { glob } from 'glob';
import path from 'path';

const parser = new DOMParser({
    onError: () => {}
});

function findHtmlFiles() {
    return glob.sync('./{project_**,templates}/**/*.html');
}

function findProjectHtmlFiles() {
    return glob.sync('./project_**/**/*.html');
}

function findProjectDirectories() {
    return glob.sync('./project_*');
}

function extractProjectId(dirPath) {
    const match = dirPath.match(/\.\/project_(\d+)/);
    return match ? parseInt(match[1]) : null;
}

// Validate project directory naming format
function validateProjectDirectoryFormat() {
    const projectDirs = findProjectDirectories();
    const invalidDirs = [];

    for (const dir of projectDirs) {
        // Project directories should follow the pattern: project_<number>_<title>
        // where <title> can include letters, numbers, underscores, and hyphens
        const regex = /^project_\d+(_[a-zA-Z0-9][a-zA-Z0-9_-]*)+$/;
        const matches = regex.test(dir);

        if (!matches) {
            invalidDirs.push(dir);
        }
    }

    return { invalidDirs };
}

// Validate project.json files
function validateProjectJson() {
    const projectDirs = findProjectDirectories();
    const missingFiles = [];
    const invalidFiles = [];
    const missingFieldsMap = new Map(); // Map to store missing fields for each directory

    for (const dir of projectDirs) {
        const projectJsonPath = path.join(dir, 'project.json');

        // Check if project.json exists
        if (!existsSync(projectJsonPath)) {
            missingFiles.push(dir);
            continue;
        }

        // Check if project.json can be parsed and has required fields
        try {
            const projectJson = JSON.parse(readFileSync(projectJsonPath, 'utf8'));

            // Define all required fields
            const requiredFields = ['id', 'title', 'description', 'short_description', 'categories', 'cover_url', 'readme', 'ides'];
            const missingFields = [];

            // Check for each required field
            for (const field of requiredFields) {
                if (!projectJson.hasOwnProperty(field)) {
                    missingFields.push(field);
                }
            }

            if (missingFields.length > 0) {
                invalidFiles.push(dir);
                missingFieldsMap.set(dir, missingFields);
            }
        } catch (error) {
            invalidFiles.push(dir);
        }
    }

    return { missingFiles, invalidFiles, missingFieldsMap };
}

// Validate HTML file naming format
function validateHtmlFileFormat() {
    const htmlFiles = findProjectHtmlFiles();
    const invalidFiles = [];

    for (const file of htmlFiles) {
        const fileName = path.basename(file);
        // HTML files in projects should follow the pattern: <order_num>_<id>_<title>.html
        // where <title> can include letters, numbers, underscores, and hyphens
        if (!fileName.match(/^\d+_\d+_[a-zA-Z0-9_-]+\.html$/)) {
            invalidFiles.push(file);
        }
    }

    return { invalidFiles };
}

// Extract metadata from HTML content
function extractMetadataFromHtml(content) {
    const metadataPattern = /<!-- Enlighter Metainfo\s*(\{.*?\})\s*-->/s;
    const match = content.match(metadataPattern);

    if (match) {
        try {
            return JSON.parse(match[1]);
        } catch (error) {
            return null;
        }
    }

    return null;
}

// Validate metadata in HTML files
function validateHtmlMetadata() {
    const htmlFiles = findProjectHtmlFiles();
    const missingMetadata = [];
    const invalidMetadata = [];
    const missingFieldsMap = new Map(); // Map to store missing fields for each file

    for (const file of htmlFiles) {
        const content = readFileSync(file, 'utf8');
        const metadata = extractMetadataFromHtml(content);

        // Check if metadata exists
        if (!metadata) {
            missingMetadata.push(file);
            continue;
        }

        // Define all required fields
        const requiredFields = ['id', 'title', 'next_button_title'];
        const missingFields = [];

        // Check for each required field
        for (const field of requiredFields) {
            if (!metadata.hasOwnProperty(field)) {
                missingFields.push(field);
            }
        }

        if (missingFields.length > 0) {
            invalidMetadata.push(file);
            missingFieldsMap.set(file, missingFields);
        }
    }

    return { missingMetadata, invalidMetadata, missingFieldsMap };
}

function extractStageId(filePath) {
    const fileName = path.basename(filePath);
    const match = fileName.match(/\d+_(\d+)_.*\.html$/);
    return match ? parseInt(match[1]) : null;
}

// Validate project IDs
function validateProjectIds() {
    const projectDirs = findProjectDirectories();
    const projectIds = new Set();
    const duplicateIds = new Set();

    for (const dir of projectDirs) {
        const id = extractProjectId(dir);
        if (id !== null) {
            if (projectIds.has(id)) {
                duplicateIds.add(id);
            } else {
                projectIds.add(id);
            }
        }
    }

    return { duplicateIds: Array.from(duplicateIds) };
}

// Validate stage IDs
function validateStageIds() {
    const htmlFiles = findHtmlFiles();
    const stageIds = new Set();
    const duplicateIds = new Set();
    const stageFilesMap = new Map(); // Map to store files with the same stage ID

    for (const file of htmlFiles) {
        const id = extractStageId(file);
        if (id !== null) {
            if (stageIds.has(id)) {
                duplicateIds.add(id);
                // Store the file path for this duplicate ID
                const existingFiles = stageFilesMap.get(id) || [];
                existingFiles.push(file);
                stageFilesMap.set(id, existingFiles);
            } else {
                stageIds.add(id);
                stageFilesMap.set(id, [file]);
            }
        }
    }

    return { duplicateIds: Array.from(duplicateIds), stageFilesMap };
}

const htmlFiles = findHtmlFiles();
const errors = [];

// Validate HTML parsing
for (const file of htmlFiles) {
    const filePath = file;

    const content = readFileSync(filePath, 'utf8');
    try {
        parser.parseFromString('<html>' + content + '</html>', 'text/html');    
    } catch (error) {
        errors.push(`Error parsing ${file}: ${error.message}`);
    }
}

// Validate project IDs
const projectIdValidation = validateProjectIds();
if (projectIdValidation.duplicateIds.length > 0) {
    errors.push(`Duplicate project IDs found: ${projectIdValidation.duplicateIds.join(', ')}`);
}

// Validate stage IDs
const stageIdValidation = validateStageIds();
if (stageIdValidation.duplicateIds.length > 0) {
    for (const id of stageIdValidation.duplicateIds) {
        const files = stageIdValidation.stageFilesMap.get(id);
        errors.push(`Duplicate stage ID ${id} found in files: ${files.join(', ')}`);
    }
}

// Validate project directory naming format
const projectDirFormatValidation = validateProjectDirectoryFormat();
if (projectDirFormatValidation.invalidDirs.length > 0) {
    for (const dir of projectDirFormatValidation.invalidDirs) {
        errors.push(`Invalid project directory name format: ${dir}. Expected format: project_<number>_<title> where <title> can include letters, numbers, underscores, and hyphens.`);
    }
}

// Validate HTML file naming format
const htmlFileFormatValidation = validateHtmlFileFormat();
if (htmlFileFormatValidation.invalidFiles.length > 0) {
    for (const file of htmlFileFormatValidation.invalidFiles) {
        errors.push(`Invalid HTML file name format: ${file}. Expected format: <order_num>_<id>_<title>.html where <title> can include letters, numbers, underscores, and hyphens.`);
    }
}

// Validate project.json files
const projectJsonValidation = validateProjectJson();
if (projectJsonValidation.missingFiles.length > 0) {
    for (const dir of projectJsonValidation.missingFiles) {
        errors.push(`Missing project.json file in directory: ${dir}`);
    }
}
if (projectJsonValidation.invalidFiles.length > 0) {
    for (const dir of projectJsonValidation.invalidFiles) {
        const missingFields = projectJsonValidation.missingFieldsMap.get(dir);
        if (missingFields && missingFields.length > 0) {
            errors.push(`Invalid project.json file in directory: ${dir}. Missing required fields: ${missingFields.join(', ')}.`);
        } else {
            errors.push(`Invalid project.json file in directory: ${dir}. File must be valid JSON and contain all required fields.`);
        }
    }
}

// Validate HTML metadata
const htmlMetadataValidation = validateHtmlMetadata();
if (htmlMetadataValidation.missingMetadata.length > 0) {
    for (const file of htmlMetadataValidation.missingMetadata) {
        errors.push(`Missing metadata in HTML file: ${file}. Each HTML file must have metadata in the format: <!-- Enlighter Metainfo { ... } -->`);
    }
}
if (htmlMetadataValidation.invalidMetadata.length > 0) {
    for (const file of htmlMetadataValidation.invalidMetadata) {
        const missingFields = htmlMetadataValidation.missingFieldsMap.get(file);
        if (missingFields && missingFields.length > 0) {
            errors.push(`Invalid metadata in HTML file: ${file}. Missing required fields: ${missingFields.join(', ')}.`);
        } else {
            errors.push(`Invalid metadata in HTML file: ${file}. Metadata must contain all required fields.`);
        }
    }
}

if (errors.length > 0) {
    console.log('Errors:');
    errors.forEach(error => console.error(error));
    process.exit(1);
} else {
    console.log('All files are valid');
}

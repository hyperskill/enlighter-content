import { DOMParser } from '@xmldom/xmldom';
import { readFileSync, readdirSync } from 'fs';
import { glob } from 'glob';

const parser = new DOMParser({
    onError: () => {}
});

function findHtmlFiles() {
    const files = glob.sync('./**/*.html');
    return files
}

const htmlFiles = findHtmlFiles();

const errors = []


for (const file of htmlFiles) {
    const filePath = file

    const content = readFileSync(filePath, 'utf8');
    try {
        const doc = parser.parseFromString('<html>' + content + '</html>', 'text/html');    
    } catch (error) {
        errors.push(`Error parsing ${file}: ${error.message}`);
    }
}


if (errors.length > 0) {
    console.log('Errors:');
    errors.forEach(error => console.error(error));
    process.exit(1);
} else {
    console.log('All files are valid');
}

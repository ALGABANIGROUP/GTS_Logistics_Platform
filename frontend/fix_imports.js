// fix_imports.js
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const baseDir = path.join(__dirname, 'src');
const extensions = ['.jsx', '.js'];
const checkedFiles = [];

function walk(dir) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      walk(fullPath);
    } else if (extensions.includes(path.extname(file))) {
      checkedFiles.push(fullPath);
    }
  });
}

function fixImports(file) {
  const content = fs.readFileSync(file, 'utf-8');
  const fixed = content.replace(/import\s+(\w+)\s+from\s+["'](.+?)["'];?/g, (match, name, relativePath) => {
    let fullPath = path.resolve(path.dirname(file), relativePath);
    const jsxPath = fullPath + '.jsx';
    const jsPath = fullPath + '.js';
    if (fs.existsSync(jsxPath)) return `import ${name} from "${relativePath}.jsx";`;
    if (fs.existsSync(jsPath)) return `import ${name} from "${relativePath}.js";`;
    console.warn(`⚠️ [${file}] Broken import: ${name} from '${relativePath}'`);
    return match;
  });

  fs.writeFileSync(file, fixed);
  console.log(`✅ Fixed imports in: ${file}`);
}

// Start scanning
walk(baseDir);
checkedFiles.forEach(fixImports);

console.log('🚀 Import fix complete.');

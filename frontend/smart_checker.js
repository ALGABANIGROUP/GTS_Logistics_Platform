// smart_checker.js
import fs from "fs";
import path from "path";

const __dirname = path.dirname(new URL(import.meta.url).pathname);
const BASE_DIR = path.resolve("./src");
const ertSound = new URL("../assets/alert.mp3", import.meta.url).href;
const extensions = [".jsx", ".js"];
const importRegex = /import\s+(?:.*?\s+from\s+)?["'](.+?)["']/g;

function getAllJSXFiles(dir) {
  let results = [];
  fs.readdirSync(dir).forEach((file) => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getAllJSXFiles(fullPath));
    } else if (extensions.includes(path.extname(fullPath))) {
      results.push(fullPath);
    }
  });
  return results;
}

function checkImports(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  let match;
  const brokenImports = [];

  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1];

    if (
      importPath.startsWith(".") || importPath.startsWith("/") // Local only
    ) {
      let resolvedPath = path.resolve(path.dirname(filePath), importPath);

      // Add extension if needed
      if (!fs.existsSync(resolvedPath)) {
        if (fs.existsSync(resolvedPath + ".js")) resolvedPath += ".js";
        else if (fs.existsSync(resolvedPath + ".jsx")) resolvedPath += ".jsx";
        else if (fs.existsSync(resolvedPath + ".ts")) resolvedPath += ".ts";
        else if (fs.existsSync(resolvedPath + ".tsx")) resolvedPath += ".tsx";
        else if (fs.existsSync(path.join(resolvedPath, "index.js"))) resolvedPath = path.join(resolvedPath, "index.js");
        else {
          brokenImports.push(importPath);
        }
      }
    }
  }

  return brokenImports;
}

// 🔎 Start scan
console.log("🔎 Scanning for broken imports in React files...\n");

const files = getAllJSXFiles(BASE_DIR);
let totalBroken = 0;

files.forEach((file) => {
  const broken = checkImports(file);
  if (broken.length > 0) {
    console.log(`❌ File: ${file}`);
    broken.forEach((imp) => {
      console.log(`   ⛔ Broken import: ${imp}`);
      totalBroken++;
    });
    console.log("");
  }
});

if (totalBroken === 0) {
  console.log("✅ No broken imports found. All clear!");
} else {
  console.log(`⚠️  Total issues found: ${totalBroken}`);
}

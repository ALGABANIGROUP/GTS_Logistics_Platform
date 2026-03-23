const fs = require("fs");
const path = require("path");

const rootDir = process.cwd(); // EN
const foldersToScan = ["frontend", "backend"];

function listFiles(dirPath, prefix = "") {
  const items = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const item of items) {
    const fullPath = path.join(dirPath, item.name);
    const relativePath = path.relative(rootDir, fullPath);

    if (item.isDirectory()) {
      console.log(`${prefix}[📁] ${relativePath}`);
      listFiles(fullPath, prefix + "  ");
    } else {
      console.log(`${prefix}- ${relativePath}`);
    }
  }
}

console.log("🧠 Project File Analysis Report:");
console.log("===============================");

foldersToScan.forEach((folder) => {
  const folderPath = path.join(rootDir, folder);
  if (fs.existsSync(folderPath)) {
    console.log(`\n🔍 Scanning: ${folder}`);
    listFiles(folderPath);
  } else {
    console.log(`⚠️ Folder not found: ${folder}`);
  }
});
console.log("\nAnalysis Complete! 🎉");
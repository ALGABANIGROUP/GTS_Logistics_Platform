#!/usr/bin/env node
// Simple scanner to block Arabic characters in repository text/code files.
// Scans the repo (excluding binaries/build caches) and fails on any match.

import fs from "fs";
import path from "path";
import { execSync } from "child_process";

const ROOT = process.cwd();
const SCAN_STAGED_ONLY = process.argv.includes("--staged");
const IGNORE_FILE = path.join(ROOT, ".arabic-lintignore");

const EXTENSIONS = new Set([
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".mjs",
    ".cjs",
    ".json",
    ".yml",
    ".yaml",
    ".ps1",
    ".bat",
    ".sql",
    ".html",
    ".css",
    ".txt",
]);

const EXCLUDE_DIRS = new Set([
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    "coverage",
    "pgdata",
    "logs",
    "__pycache__",
]);

// Legacy paths that intentionally contain Arabic content.
// Keep this list explicit to preserve strict linting in active code paths.
const EXCLUDE_PATH_PREFIXES = [
    "GTS_Logistics_Platform/",
    "trainer_bot_advanced/",
    "scripts/seed_",
    "scripts/from fastapi import apirouter, depends.ps1",
    "pre_upload_audit",
    "run_telegram_bot.py",
];

function loadIgnorePrefixes() {
    if (!fs.existsSync(IGNORE_FILE)) {
        return [];
    }

    try {
        return fs
            .readFileSync(IGNORE_FILE, "utf8")
            .split(/\r?\n/)
            .map((line) => line.trim())
            .filter(Boolean)
            .filter((line) => !line.startsWith("#"))
            .map((line) => line.replace(/\\/g, "/"));
    } catch (error) {
        console.warn(`[arabic-lint] WARN: failed to read .arabic-lintignore: ${error.message}`);
        return [];
    }
}

const IGNORE_PATH_PREFIXES = [...EXCLUDE_PATH_PREFIXES, ...loadIgnorePrefixes()];

// Arabic Unicode ranges
const ARABIC_REGEX = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;

function toRelativePosix(filePath) {
    return path.relative(ROOT, filePath).replace(/\\/g, "/");
}

function isExcludedPath(filePath) {
    const rel = toRelativePosix(filePath).toLowerCase();
    return IGNORE_PATH_PREFIXES.some((prefix) => rel.startsWith(prefix.toLowerCase()));
}

/** Recursively walk and yield file paths */
function* walk(dir) {
    let list;
    try {
        list = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
        return;
    }
    for (const entry of list) {
        const full = path.join(dir, entry.name);
        if (isExcludedPath(full)) continue;
        if (entry.isDirectory()) {
            if (EXCLUDE_DIRS.has(entry.name)) continue;
            yield* walk(full);
        } else {
            const ext = path.extname(entry.name).toLowerCase();
            if (EXTENSIONS.has(ext)) yield full;
        }
    }
}

function getStagedFiles() {
    let output = "";
    try {
        output = execSync("git diff --cached --name-only --diff-filter=ACMR", {
            cwd: ROOT,
            encoding: "utf8",
            stdio: ["ignore", "pipe", "ignore"],
        });
    } catch {
        return [];
    }

    const files = output
        .split(/\r?\n/)
        .map((p) => p.trim())
        .filter(Boolean)
        .map((p) => path.resolve(ROOT, p))
        .filter((absPath) => !isExcludedPath(absPath))
        .filter((absPath) => {
            if (!fs.existsSync(absPath)) return false;
            const ext = path.extname(absPath).toLowerCase();
            return EXTENSIONS.has(ext);
        });

    return files;
}

function scanFile(file) {
    const text = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, '');
    if (!ARABIC_REGEX.test(text)) return null;
    const lines = text.split(/\r?\n/);
    const hits = [];
    for (let i = 0; i < lines.length; i++) {
        if (ARABIC_REGEX.test(lines[i])) {
            hits.push({ line: i + 1, preview: lines[i].slice(0, 200) });
        }
    }
    return { file, hits };
}

function main() {
    const findings = [];

    if (SCAN_STAGED_ONLY) {
        const stagedFiles = getStagedFiles();
        if (stagedFiles.length === 0) {
            console.log("[arabic-lint] OK: no staged text files to scan.");
            return;
        }

        for (const file of stagedFiles) {
            const res = scanFile(file);
            if (res) findings.push(res);
        }
    } else {
        if (fs.existsSync(ROOT)) {
            for (const file of walk(ROOT)) {
                const res = scanFile(file);
                if (res) findings.push(res);
            }
        }
    }

    if (findings.length === 0) {
        const mode = SCAN_STAGED_ONLY ? "staged files" : "repository";
        console.log(`[arabic-lint] OK: no Arabic characters found in ${mode}.`);
        return;
    }

    console.error("[arabic-lint] ERROR: Arabic characters are not allowed in this repository.");
    for (const f of findings) {
        console.error(`\n- ${path.relative(ROOT, f.file)}`);
        for (const h of f.hits.slice(0, 5)) {
            console.error(`  Line ${h.line}: ${h.preview}`);
        }
        if (f.hits.length > 5) {
            console.error(`  ...and ${f.hits.length - 5} more lines`);
        }
    }
    process.exit(1);
}

main();

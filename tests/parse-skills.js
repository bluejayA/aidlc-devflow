#!/usr/bin/env node

/**
 * parse-skills.js — SKILL.md meta tag parser
 *
 * Extracts @gate, @gate-option, @step, and @condition meta tags
 * from SKILL.md files and outputs JSON graph files.
 *
 * Usage: node tests/parse-skills.js [--skills-dir skills] [--output-dir tests/graph]
 */

import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from "fs";
import { join, basename, resolve } from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const projectRoot = resolve(__dirname, "..");

// Parse CLI args
const args = process.argv.slice(2);
let skillsDir = join(projectRoot, "skills");
let outputDir = join(__dirname, "graph");

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--skills-dir" && args[i + 1]) {
    skillsDir = resolve(args[++i]);
  } else if (args[i] === "--output-dir" && args[i + 1]) {
    outputDir = resolve(args[++i]);
  }
}

// Path boundary check: directories must be within project root
for (const [name, dir] of [["skills-dir", skillsDir], ["output-dir", outputDir]]) {
  if (!resolve(dir).startsWith(projectRoot)) {
    console.error(`ERROR: ${name} must be within project root (${projectRoot})`);
    process.exit(1);
  }
}

// Tag regex patterns (match the Python test patterns)
const GATE_RE = /^<!--\s*@gate:\s+(\S+)\s*-->$/;
const GATE_OPTION_RE =
  /^<!--\s*@gate-option:\s+(\S+)\s+->\s+(\S+)(?:\s+\{([^}]*)\})?\s*-->$/;
const STEP_RE =
  /^<!--\s*@step:(\d+)\s+id=(\S+)(?:\s+skip-when=(\S+))?\s*-->$/;
const CONDITION_RE = /^<!--\s*@condition:\s+(.+?)\s+->\s+(\S+)\s*-->$/;

/**
 * Parse a single SKILL.md file and extract meta tags.
 * @param {string} filePath - Path to SKILL.md
 * @returns {object} Parsed graph object
 */
function parseSkill(filePath) {
  const content = readFileSync(filePath, "utf-8");
  const lines = content.split("\n");

  // Extract skill name from directory name
  const dirName = basename(resolve(filePath, ".."));
  const name = dirName;

  const steps = [];
  const gates = [];
  const conditions = [];

  let currentGate = null;
  let inCodeBlock = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();

    // Track fenced code blocks — skip tags inside them
    if (line.startsWith("```")) {
      inCodeBlock = !inCodeBlock;
      continue;
    }
    if (inCodeBlock) continue;

    // Check @gate (must come before @gate-option check)
    const gateMatch = GATE_RE.exec(line);
    if (gateMatch) {
      // Flush previous gate if exists
      if (currentGate) {
        gates.push(currentGate);
      }
      currentGate = {
        id: gateMatch[1],
        options: [],
      };
      continue;
    }

    // Check @gate-option
    const optionMatch = GATE_OPTION_RE.exec(line);
    if (optionMatch) {
      const option = {
        option: optionMatch[1],
        target: optionMatch[2],
        condition: optionMatch[3] || null,
      };
      if (currentGate) {
        currentGate.options.push(option);
      }
      continue;
    }

    // Check @step
    const stepMatch = STEP_RE.exec(line);
    if (stepMatch) {
      steps.push({
        order: parseInt(stepMatch[1], 10),
        id: stepMatch[2],
        skipWhen: stepMatch[3] || null,
      });
      continue;
    }

    // Check @condition
    const condMatch = CONDITION_RE.exec(line);
    if (condMatch) {
      conditions.push({
        expr: condMatch[1],
        target: condMatch[2],
      });
      continue;
    }
  }

  // Flush last gate
  if (currentGate) {
    gates.push(currentGate);
  }

  return { name, steps, gates, conditions };
}

/**
 * Find all SKILL.md files in the skills directory.
 * @param {string} dir - Skills directory path
 * @returns {string[]} Array of SKILL.md file paths
 */
function findSkillFiles(dir) {
  const results = [];

  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    if (!statSync(fullPath).isDirectory()) continue;

    const skillFile = join(fullPath, "SKILL.md");
    try {
      statSync(skillFile);
      results.push(skillFile);
    } catch {
      // No SKILL.md in this directory, skip
    }
  }

  return results;
}

// Main
mkdirSync(outputDir, { recursive: true });

const skillFiles = findSkillFiles(skillsDir);
let parsedCount = 0;

for (const filePath of skillFiles) {
  const graph = parseSkill(filePath);

  // Only output files that have at least one meta tag
  if (
    graph.steps.length > 0 ||
    graph.gates.length > 0 ||
    graph.conditions.length > 0
  ) {
    const outputPath = join(outputDir, `${graph.name}.json`);
    // Preserve externalRefs from existing JSON if present
    try {
      const existing = JSON.parse(readFileSync(outputPath, "utf-8"));
      if (existing.externalRefs) {
        graph.externalRefs = existing.externalRefs;
      }
    } catch (_) { /* file doesn't exist yet, skip */ }
    writeFileSync(outputPath, JSON.stringify(graph, null, 2) + "\n");
    parsedCount++;
  }
}

console.log(
  `Parsed ${skillFiles.length} SKILL.md files, generated ${parsedCount} graph(s) in ${outputDir}`
);

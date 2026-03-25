import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const repoRoot = process.cwd();
const promptsPath = path.join(repoRoot, 'viewer', 'prompts.js');
const indexPath = path.join(repoRoot, 'viewer', 'index.html');

function loadPromptExports() {
  const source = fs.readFileSync(promptsPath, 'utf8');
  const wrapped = `${source}

globalThis.__promptExports = {
  buildExtractionPrompt,
  PDF_SCHEMA,
  DOCX_SCHEMA,
  IMAGE_SCHEMA,
  SPREADSHEET_SCHEMA
};`;

  const context = {
    console,
    globalThis: {},
  };
  context.global = context;
  vm.createContext(context);
  new vm.Script(wrapped, { filename: promptsPath }).runInContext(context);
  return context.globalThis.__promptExports;
}

test('extraction schemas and prompts omit removed NDE fields', () => {
  const {
    buildExtractionPrompt,
    PDF_SCHEMA,
    DOCX_SCHEMA,
    IMAGE_SCHEMA,
    SPREADSHEET_SCHEMA,
  } = loadPromptExports();

  const removedFields = ['equipment', 'cmls', 'alerts', 'personnel', 'codes'];
  const prompt = buildExtractionPrompt('spreadsheet', {
    preExtractedText: 'sample spreadsheet text',
  });

  for (const field of removedFields) {
    assert.equal(
      PDF_SCHEMA.includes(`"${field}"`),
      false,
      `PDF schema should not include ${field}`,
    );
    assert.equal(
      DOCX_SCHEMA.includes(`"${field}"`),
      false,
      `DOCX schema should not include ${field}`,
    );
    assert.equal(
      IMAGE_SCHEMA.includes(`"${field}"`),
      false,
      `IMAGE schema should not include ${field}`,
    );
    assert.equal(
      SPREADSHEET_SCHEMA.includes(`"${field}"`),
      false,
      `Spreadsheet schema should not include ${field}`,
    );
    assert.equal(
      prompt.includes(`${field}:`),
      false,
      `Spreadsheet prompt rules should not mention ${field}`,
    );
  }
});

test('viewer extraction post-processing does not normalize removed fields', () => {
  const source = fs.readFileSync(indexPath, 'utf8');
  const removedAssignments = [
    'extraction.equipment = extraction.equipment || [];',
    'extraction.cmls = extraction.cmls || [];',
    'extraction.alerts = extraction.alerts || [];',
    'extraction.personnel = extraction.personnel || [];',
    'extraction.codes = extraction.codes || [];',
  ];

  for (const assignment of removedAssignments) {
    assert.equal(
      source.includes(assignment),
      false,
      `index.html should not contain "${assignment}"`,
    );
  }
});

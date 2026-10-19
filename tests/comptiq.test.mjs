import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';

const read = name => JSON.parse(readFileSync(new URL('../data/' + name, import.meta.url), 'utf8'));
const data = read('games.json');
const company = read('company-coverage.json').companies.find(c => c.id === 'comptiq');
const rows = read('gameplay-catalogues.json').companies.comptiq.groups.flatMap(g => g.rows);

test('Comptiq text-input adventure is searchable in the main catalogue without a duplicate', () => {
  assert.deepEqual(company.workIds, ['g111']);
  assert.deepEqual(company.legacyCommandWorkIds, ['g111']);
  assert.deepEqual(filterCatalogue(data, {company: 'コンプティーク', interaction: '文字输入'}).map(x => x.work.id), ['g111']);
  assert.equal(data.works.filter(w => w.originalTitle === 'カムイの剣').length, 1);
  assert.equal(data.contentVersions.filter(c => c.workId === 'g111').length, 1);
  assert.deepEqual(data.platformReleases.filter(r => r.workId === 'g111').map(r => r.platform).sort(), ['FM-7', 'PC-8801']);
  assert.match(data.works.find(w => w.id === 'g111').interactionNote, /动词＋名词/);
});

test('dossier links the main work once and keeps other catalogue rows as references', () => {
  const page = readFileSync(new URL('../comptiq.html', import.meta.url), 'utf8');
  assert.equal(page.split('class="card" id="g111"').length - 1, 1);
  assert.equal(rows.length, 23);
  assert.deepEqual(rows.filter(r => r.workId).map(r => r.workId), ['g111']);
  assert.ok(page.includes('主库文字输入叙事作品'));
});

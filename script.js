/* Interface layer: collect filters, call the Python API, and render the main views. */
'use strict';
const $ = (selector) => document.querySelector(selector);
const state = {page: 1, pages: 1, total: 0, result: null, metadata: null, imageOnly: true, era: '', group: '', request: 0};
const viewNames = ['explore', 'detail', 'insights', 'about'];
const fieldNames = ['q', 'source', 'category', 'material', 'place', 'year_start', 'year_end'];
const form = $('#search-form');
function node(tag, className, text) { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; }
function external(url) { try { const parsed = new URL(url); return parsed.protocol === 'https:' ? parsed.href : ''; } catch { return ''; } }
function rightsLabel(record) { const value=String(record.image_licence||'').trim(); return value?`Source rights label: ${value}`:'Check the source record for image conditions'; }
async function api(path) {
  const response = await fetch(path, {headers: {'Accept': 'application/json'}});
  const payload = await response.json();
  if (!response.ok) throw new Error(typeof payload.error === 'string' ? payload.error : 'The request failed. Please try again.');
  return payload;
}
function params() {
  const data = new FormData(form); const query = new URLSearchParams();
  fieldNames.forEach(key => { const value = String(data.get(key) || '').trim(); if (value) query.set(key, value); });
  query.set('image_only', String(state.imageOnly)); if (state.era) query.set('era', state.era); if (state.group) query.set('group', state.group); query.set('sort', $('#sort').value); query.set('page', String(state.page)); query.set('page_size', '12'); return query;
}
function message(text, error = false) { $('#status').textContent = text; $('#status').classList.toggle('error', error); }
function validYears() {
  const start = $('#year-start').value, end = $('#year-end').value;
  for (const value of [start, end]) if (value && (!/^\d+$/.test(value) || +value < 1 || +value > 2100)) { message('Enter a whole year from 1 to 2100.', true); return false; }
  if (start && end && +start > +end) { message('The start year must not be later than the end year.', true); return false; }
  return true;
}
function imagePanel(record, className) {
  const box = node('div', className);
  const url = external(record.image_url);
  if (url) {
    const img = node('img'); img.src = url; img.alt = record.title; img.loading = 'eager'; img.referrerPolicy = 'no-referrer';
    img.addEventListener('error', () => { box.replaceChildren(node('span', 'feature-placeholder', 'Image unavailable'), node('small', '', 'The catalogue record is still available.')); box.classList.remove('has-image'); }, {once:true});
    box.append(img); box.classList.add('has-image');
  } else box.append(node('span', 'detail-index', record.id), node('span', '', 'PUBLIC CATALOGUE'));
  return box;
}
function card(record, index) {
  const a = node('a', 'record-card'); a.title = record.title; a.href = `#object/${encodeURIComponent(record.id)}`;
  let cover;
  if (record.image_url) cover = imagePanel(record, 'record-cover');
  else { cover = node('div', 'record-cover'); cover.append(node('span', 'cover-label', record.identifier || record.id), node('span', 'cover-number', String(index + 1 + (state.page - 1) * 12).padStart(2, '0')), node('span', 'cover-category', record.category)); }
  const body = node('div', 'record-body'); body.append(node('div', 'record-meta', `${record.category} · ${record.date || 'Date not recorded'}`), node('h3', 'record-title', record.title));
  const bottom = node('div', 'record-bottom'); bottom.append(node('span', '', record.source_name), node('span', '', 'View record')); body.append(bottom); if(record.image_url)body.append(node('small','card-credit',`${record.source_name.includes('Western Australia')?'SLWA':'NMA'} · ${rightsLabel(record)}`)); a.append(cover, body); return a;
}
function populateFacets(facets) {
  [['source','sources','All sources'],['category','categories','All categories'],['material','materials','All materials'],['place','places','All places']].forEach(([id, key, label]) => {
    const select = $(`#${id}`); const value = select.value; select.replaceChildren(new Option(label, ''));
    (facets[key] || []).forEach(entry => { const option = typeof entry === 'string' ? entry : entry.label; select.add(new Option(option, option)); }); select.value = value;
  });
}
function syncPills() { document.querySelectorAll('[data-era]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.era===state.era))); document.querySelectorAll('[data-group]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.group===state.group))); }
async function search({resetPage = true, scroll = false} = {}) {
  if (!validYears()) return;
  if (resetPage) state.page = 1;
  const request = ++state.request; $('#collection-grid').setAttribute('aria-busy', 'true'); message('Searching the catalogue…');
  try {
    const result = await api(`/api/collections?${params()}`); if (request !== state.request) return;
    state.result = result; state.page = result.page; state.pages = result.pages; state.total = result.total;
    populateFacets(result.facets); syncPills();
    $('#collection-grid').hidden = !state.imageOnly; $('#table-wrap').hidden = state.imageOnly || !result.total;
    if (state.imageOnly) $('#collection-grid').replaceChildren(...result.items.map(card)); else renderTable(result.items); $('#empty').hidden = result.total !== 0;
    const start = result.total ? (result.page - 1) * result.page_size + 1 : 0;
    const end = Math.min(result.page * result.page_size, result.total);
    $('#results-summary').textContent = `Illustrated collection · ${result.total} ${result.total === 1 ? 'record' : 'records'} · ${start}–${end}`;
    $('#page-info').textContent = `Page ${result.page} of ${Math.max(result.pages, 1)}`;
    $('#previous').disabled = result.page <= 1; $('#next').disabled = result.page >= result.pages;
    message(''); renderStats(result.stats);
    if (scroll) $('#catalogue-heading').scrollIntoView({block:'start'});
  } catch (error) {
    if (request !== state.request) return;
    message(`Could not load records. ${error.message}`, true); $('#results-summary').textContent = 'Search failed. Change your filters or try again.';
    $('#collection-grid').replaceChildren(); $('#table-wrap').hidden = true; $('#record-table tbody').replaceChildren(); $('#empty').hidden = true; $('#previous').disabled = true; $('#next').disabled = true;
    state.result = null; $('#stats-summary').replaceChildren(); $('#category-chart').textContent = 'Complete a search in Explore to see insights.'; $('#decade-chart').replaceChildren();
  } finally { if (request === state.request) $('#collection-grid').setAttribute('aria-busy', 'false'); }
}
function renderTable(records) {
  const body = $('#record-table tbody');body.replaceChildren();
  records.forEach(r => {const tr=node('tr');const title=node('td');const link=node('a','',r.title);link.href=`#object/${encodeURIComponent(r.id)}`;title.append(link);tr.append(title,node('td','',r.source_name),node('td','',r.category),node('td','',r.date||'Not recorded'),node('td','',r.identifier));body.append(tr);});
}
function measurementText(value) {
  if (!value || typeof value !== 'object') return 'Not recorded';
  const unit = typeof value.unitText === 'string' ? value.unitText : '';
  const labels = {height:'Height',width:'Width',depth:'Depth',length:'Length',diameter:'Diameter',weight:'Weight'};
  const parts = Object.entries(labels).filter(([key]) => value[key] !== undefined && value[key] !== null && value[key] !== '').map(([key,label]) => `${label} ${value[key]}${unit ? ` ${unit}` : ''}`);
  return parts.length ? parts.join(' · ') : 'Not recorded';
}
function sourceSection(parent, heading, content, options = {}) {
  if (!content || !String(content).trim()) return;
  const section = node(options.details ? 'details' : 'section', 'source-section');
  if (options.details) section.append(node('summary','',heading)); else section.append(node('h2','',heading));
  const body = node('p','source-copy',String(content)); section.append(body); parent.append(section);
}
function reset() { HTMLFormElement.prototype.reset.call(form); state.era=''; state.group=''; $('#sort').value = 'relevance'; syncPills(); search(); }
function bars(target, rows) {
  target.replaceChildren(); if (!rows.length) { target.append(node('p', '', 'No records to summarise for these filters.')); return; }
  const max = Math.max(...rows.map(row => row.count));
  rows.forEach(row => { const item = node('div', 'bar-row'); const label = node('div', 'bar-label'); label.append(node('span','',row.label), node('strong','',String(row.count))); const track = node('div','bar-track'); track.setAttribute('aria-hidden','true'); const fill = node('div','bar-fill'); fill.style.width = `${max ? row.count / max * 100 : 0}%`; track.append(fill); item.append(label, track); target.append(item); });
}
function renderStats(stats) {
  const summary = $('#stats-summary'); summary.replaceChildren();
  [[state.imageOnly?'Illustrated matches':'Catalogue matches',stats.total],['Usable production year',stats.dated],['Unknown production year',stats.undated]].forEach(([title,count]) => { const el = node('div','stat-block'); el.append(node('span','',title),node('strong','',String(count)));summary.append(el); });
  bars($('#category-chart'),stats.categories.slice(0,10)); bars($('#decade-chart'),stats.decades);
}
let detailRequest = 0;
async function detail(id) {
  const seq = ++detailRequest; const target = $('#detail-content'); target.replaceChildren(node('p','','Loading the object record…'));
  try {
    const r = await api(`/api/objects/${encodeURIComponent(id)}`); if (seq !== detailRequest) return;
    const layout = node('div','detail-layout'); const visualColumn = node('div'); visualColumn.append(imagePanel(r,'detail-visual'));
    if(r.image_url) { const zoom=node('button','zoom-button','Enlarge image');zoom.type='button';zoom.addEventListener('click',()=>{$('#zoom-image').src=external(r.image_large_url||r.image_url);$('#zoom-image').alt=r.title;$('#image-dialog-title').textContent=r.title;$('#zoom-credit').textContent=`${r.source_name} · ${rightsLabel(r)}`;$('#image-dialog').showModal();});visualColumn.append(zoom); }
    if (r.image_url) { const credit = node('p','image-credit',`Image: ${r.source_name} · ${rightsLabel(r)} · `); const link=node('a','','Original image');link.href=external(r.image_url);link.target='_blank';link.rel='noopener noreferrer';credit.append(link);visualColumn.append(credit); }
    else visualColumn.append(node('p','image-credit','This record contains public catalogue text. Follow the source for images and context.'));
    const text = node('article'); text.append(node('p','eyebrow',`SOURCE RECORD / ${r.identifier||r.id}`)); const heading = node('h1','detail-heading',r.title);heading.id='detail-heading';heading.tabIndex=-1;text.append(heading);
    const dl = node('dl','detail-facts');
    const entries=[['Source institution',r.source_name],['Category',r.category],['Accession number',r.identifier||'Not recorded'],['Production date',r.date ? `${r.date} (${r.date_role || 'Production'})`:'Not recorded'],['Materials',r.materials.join(' / ')||'Not recorded'],['Measurements',measurementText(r.measurements)],['Places & relationships',r.places.join(' · ')||'Not recorded'],['Collection',r.collection||'Not recorded'],['Record updated',r.modified||'Not recorded'],['Text licence',r.licence||'See source record']];
    entries.forEach(([label,value])=>dl.append(node('dt','',label),node('dd','',value))); text.append(dl);
    const published = node('div','published-record');
    sourceSection(published,'Published description',r.description);
    sourceSection(published,'Physical description',r.physical_description);
    sourceSection(published,'Significance statement',r.significance_statement,{details:true});
    sourceSection(published,'Educational significance',r.educational_significance,{details:true});
    if (Array.isArray(r.related_dates) && r.related_dates.length) {
      const lines=r.related_dates.map(item=>[item.title,item.roleName].filter(Boolean).join(' — ')).filter(Boolean);
      sourceSection(published,'Related dates',lines.join('\n'));
    }
    if (r.acknowledgement) sourceSection(published,'Acknowledgement',r.acknowledgement);
    if (Array.isArray(r.related_links) && r.related_links.length) {
      const section=node('section','source-section');section.append(node('h2','','Related source resources'));const list=node('ul','related-links');
      r.related_links.forEach(item=>{const href=external(item.identifier);if(!href)return;const li=node('li');const a=node('a','',item.title||'Related museum resource');a.href=href;a.target='_blank';a.rel='noopener noreferrer';li.append(a);list.append(li);});
      if(list.children.length){section.append(list);published.append(section);}
    }
    if (!published.children.length) sourceSection(published,'About this record','No additional descriptive text was supplied in this API snapshot. Use the museum record below to check for later updates.');
    text.append(published);
    const actions=node('div','detail-actions'); const sourceHref=external(r.source_url); const sourceIsDataset=/catalogue\.data\.wa\.gov\.au/i.test(sourceHref); const original=node('a','primary',sourceIsDataset?'View source dataset':'View source record');original.href=sourceHref;original.target='_blank';original.rel='noopener noreferrer';actions.append(original);text.append(actions,node('p','image-credit',`${r.source_copyright||`Original titles and catalogue fields © ${r.source_name}`}. Historical wording is retained.`));
    layout.append(visualColumn,text);target.replaceChildren(layout);heading.focus({preventScroll:true});
  } catch(error) { if (seq !== detailRequest) return; target.replaceChildren(node('h1','detail-heading','Record not found'),node('p','',`Return to the collection and choose a record. ${error.message}`)); }
}
function route() {
  const hash = location.hash.slice(1) || 'explore'; const name = hash.startsWith('object/') ? 'detail' : ['explore','insights','about'].includes(hash) ? hash : 'explore';
  viewNames.forEach(view => $(`#${view}-view`).hidden = view !== name);
  document.querySelectorAll('[data-nav]').forEach(link => { const active=link.dataset.nav === (name === 'detail' ? 'explore' : name);link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current'); });
  if (name === 'detail') { try { detail(decodeURIComponent(hash.slice(7))); } catch { detail(hash.slice(7)); } }
  else if (name === 'insights' && state.result) renderStats(state.result.stats);
  if (name !== 'explore') { window.scrollTo(0,0); $(`#${name}-heading`)?.focus({preventScroll:true}); }
  document.title = `${{explore:'Explore',detail:'Object record',insights:'Insights',about:'Sources & language'}[name]} · Collection Explorer`;
}
form.addEventListener('submit', event => { event.preventDefault(); search(); });
['source','category','material','place'].forEach(id => $(`#${id}`).addEventListener('change',()=>search()));
$('#sort').addEventListener('change',()=>search()); $('#reset').addEventListener('click',reset);$('#empty-reset').addEventListener('click',reset);
document.querySelectorAll('[data-era]').forEach(button=>button.addEventListener('click',()=>{state.era=button.dataset.era;syncPills();search();}));
document.querySelectorAll('[data-group]').forEach(button=>button.addEventListener('click',()=>{state.group=button.dataset.group;syncPills();search();}));
$('#previous').addEventListener('click',()=>{if(state.page>1){state.page--;search({resetPage:false,scroll:true});}});
$('#next').addEventListener('click',()=>{if(state.page<state.pages){state.page++;search({resetPage:false,scroll:true});}});
$('#toggle-filters').addEventListener('click',()=>{const hidden=!$('#advanced-filters').hidden;$('#advanced-filters').hidden=hidden;$('#toggle-filters').setAttribute('aria-expanded',String(!hidden));$('#toggle-filters').firstChild.textContent=hidden?'More filters ':'Fewer filters ';});
$('#close-image').addEventListener('click',()=>$('#image-dialog').close());$('#zoom-image').addEventListener('error',()=>{$('#zoom-credit').textContent='The large image could not load. Close this window and use the original image link.';});
window.addEventListener('hashchange',route);
async function init() {
  route();
  if (location.protocol==='file:') { message('Run python app.py (or python3 app.py on macOS) in the VS Code terminal, then open http://127.0.0.1:8000. Search and insights require the Python server.',true);$('#results-summary').textContent='Start the Python application to continue';$('#collection-grid').setAttribute('aria-busy','false');return; }
  try { const meta=await api('/api/meta');state.metadata=meta;$('#hero-count').textContent=String(meta.count??meta.record_count);$('#gallery-count').textContent=meta.image_count;$('#retrieved-at').textContent=meta.retrieved_at;$('#nma-count-label').textContent=meta.nma_count||0;$('#slwa-count-label').textContent=meta.slwa_count||0;const coverage=meta.field_coverage||{};$('#source-counts').textContent=`This catalogue contains ${meta.count??meta.record_count} records: ${meta.nma_count||0} from NMA and ${meta.slwa_count||0} from SLWA. Of these, ${meta.image_count||0} include a non-empty image URL and ${(meta.count??meta.record_count)-(meta.image_count||0)} are text-only. ${coverage.description||0} records include a published description or summary. Missing fields remain visible as missing data.`; }
  catch(error){message(`Data service unavailable: ${error.message}`,true);}
  await search();
  try { const r=await api('/api/objects/124001'); if(r.image_url) {const box=imagePanel(r,'feature-image');box.id='feature-image';$('#feature-image').replaceWith(box);} } catch { /* Collection details remain available from the results list. */ }
}
init();

const $ = id => document.getElementById(id);
const dateSelect = $('snapshot-date');
const periodSelect = $('period');
const searchInput = $('search');
const languageSelect = $('language');
const controls = [dateSelect, periodSelect, searchInput, languageSelect];
const number = value => typeof value === 'number' && Number.isFinite(value) ? new Intl.NumberFormat('en-US').format(value) : '未提供';
const periodName = period => period === 'weekly' ? '週榜' : '月榜';
let snapshots = [];
let lastDetailButton = null;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function githubLink(url, label) {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || parsed.hostname !== 'github.com' || parsed.port || parsed.username || parsed.password) return null;
    const link = element('a', label);
    link.href = parsed.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    return link;
  } catch {
    return null;
  }
}

function currentSnapshot() {
  return snapshots.find(snapshot => snapshot.date === dateSelect.value);
}

function closeDetails(returnFocus = false) {
  $('details').hidden = true;
  if (lastDetailButton) {
    lastDetailButton.setAttribute('aria-expanded', 'false');
    if (returnFocus && lastDetailButton.isConnected) lastDetailButton.focus();
  }
  lastDetailButton = null;
}

function fillLanguages() {
  const previous = languageSelect.value;
  languageSelect.replaceChildren(new Option('所有語言', ''));
  const languages = [...new Set(currentSnapshot()[periodSelect.value].map(item => item.language || '未標示'))].sort();
  for (const language of languages) languageSelect.add(new Option(language, language));
  languageSelect.value = languages.includes(previous) ? previous : '';
}

function showDetails(item, button) {
  closeDetails();
  lastDetailButton = button;
  button.setAttribute('aria-expanded', 'true');
  $('detail-title').textContent = item.full_name;
  $('detail-description').textContent = item.description || '來源未提供描述。';
  const facts = $('detail-facts');
  facts.replaceChildren(
    element('p', `語言：${item.language || '未標示'}`),
    element('p', `累計 stars：${number(item.total_stars)}`),
    element('p', `Forks：${number(item.forks)}`),
  );
  const link = githubLink(item.url, '在 GitHub 開啟專案');
  facts.append(link || element('p', '來源未提供有效的 GitHub 專案連結。'));
  const history = $('history-body');
  history.replaceChildren();
  for (const snapshot of snapshots) {
    for (const period of ['weekly', 'monthly']) {
      const observed = snapshot[period].find(repo => repo.full_name === item.full_name);
      const row = element('tr');
      row.dataset.date = snapshot.date;
      row.dataset.period = period;
      row.append(
        element('th', `${snapshot.date} · ${periodName(period)}`),
        element('td', observed ? String(observed.rank) : '—'),
        element('td', observed ? number(observed.period_stars) : '未觀測'),
      );
      row.firstChild.scope = 'row';
      const source = element('td');
      source.append(githubLink(snapshot.source_url, '來源') || element('span', '未提供'));
      row.append(source);
      history.append(row);
    }
  }
  $('details').hidden = false;
  $('detail-title').focus({ preventScroll: true });
  $('details').scrollIntoView({ block: 'start' });
}

function render() {
  closeDetails();
  const snapshot = currentSnapshot();
  const period = periodSelect.value;
  const query = searchInput.value.trim().toLocaleLowerCase();
  const items = snapshot[period];
  const filtered = items.filter(item => {
    const text = `${item.full_name} ${item.description || ''}`.toLocaleLowerCase();
    return text.includes(query) && (!languageSelect.value || (item.language || '未標示') === languageSelect.value);
  });
  $('list-title').textContent = `${snapshot.date} ${periodName(period)}`;
  $('stars-heading').textContent = period === 'weekly' ? '本週新增 stars' : '本月新增 stars';
  $('result-count').textContent = `顯示 ${filtered.length} / ${items.length} 個專案`;
  const provenance = $('provenance');
  provenance.replaceChildren(element('span', `擷取時間（台北） ${snapshot.generated_at_taipei}`));
  provenance.append(element('span', `Commit ${snapshot.commit.slice(0, 12)}`, 'commit'));
  provenance.append(githubLink(snapshot.source_url, '查看快照原始來源') || element('span', '來源連結無效'));
  const body = $('repo-body');
  body.replaceChildren();
  for (const item of filtered) {
    const row = element('tr');
    row.append(element('td', String(item.rank).padStart(2, '0'), 'rank'));
    const repo = element('th', undefined, 'repo');
    repo.scope = 'row';
    repo.append(element('span', item.full_name, 'repo-name'), element('p', item.description || '來源未提供描述。', 'description'));
    const language = element('td', item.language || '未標示', 'language');
    language.dataset.label = '語言';
    const stars = element('td', number(item.period_stars), 'period-stars');
    stars.dataset.label = period === 'weekly' ? '本週新增' : '本月新增';
    const action = element('td', undefined, 'action');
    const button = element('button', '查看詳情');
    button.type = 'button';
    button.setAttribute('aria-label', `查看 ${item.full_name} 詳情`);
    button.setAttribute('aria-controls', 'details');
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', () => showDetails(item, button));
    action.append(button);
    row.append(repo, language, stars, action);
    body.append(row);
  }
  $('empty-state').hidden = filtered.length > 0;
  $('repo-table').hidden = filtered.length === 0;
}

async function load() {
  controls.forEach(control => { control.disabled = true; });
  $('load-state').hidden = false;
  $('error-state').hidden = true;
  $('retry').disabled = true;
  try {
    const response = await fetch('../data/index.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.snapshots) || !data.snapshots.length || !data.snapshots.every(snapshot => typeof snapshot.date === 'string' && typeof snapshot.commit === 'string' && Array.isArray(snapshot.weekly) && Array.isArray(snapshot.monthly))) throw new Error('Invalid snapshots');
    snapshots = [...data.snapshots].sort((a, b) => a.date.localeCompare(b.date));
    dateSelect.replaceChildren();
    for (const snapshot of snapshots) dateSelect.add(new Option(snapshot.date, snapshot.date));
    dateSelect.value = snapshots.at(-1).date;
    $('date-range').textContent = `${snapshots[0].date} — ${snapshots.at(-1).date}`;
    fillLanguages();
    render();
    controls.forEach(control => { control.disabled = false; });
  } catch {
    $('error-state').hidden = false;
    $('date-range').textContent = '快照尚未載入';
  } finally {
    $('load-state').hidden = true;
    $('retry').disabled = false;
  }
}

for (const select of [dateSelect, periodSelect]) select.addEventListener('change', () => { fillLanguages(); render(); });
searchInput.addEventListener('input', render);
languageSelect.addEventListener('change', render);
$('close-detail').addEventListener('click', () => closeDetails(true));
$('clear-filters').addEventListener('click', () => {
  searchInput.value = '';
  languageSelect.value = '';
  render();
  searchInput.focus();
});
$('retry').addEventListener('click', load);
load();

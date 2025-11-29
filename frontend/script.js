const tasks = [];

function renderResults(list){
  const out = document.getElementById('results');
  out.innerHTML = '';
  list.forEach(t => {
    const div = document.createElement('div');
    div.className = 'task';
    const score = t.score || 0;
    if(score >= 70) div.classList.add('high');
    else if(score >=40) div.classList.add('medium');
    else div.classList.add('low');
    div.innerHTML = `<strong>${t.title || t._key}</strong> — Score: ${score}<br/>
      <small>Due: ${t.due_date || 'N/A'} • Est hrs: ${t.estimated_hours || 'N/A'} • Importance: ${t.importance || 'N/A'}</small>
      <div><em>Why:</em> ${ (t.explanation && t.explanation.notes) ? t.explanation.notes.join('; ') : 'Calculated from factors' }</div>
      <pre>${JSON.stringify(t.explanation || {}, null, 2)}</pre>`;
    out.appendChild(div);
  });
}

document.getElementById('taskForm').addEventListener('submit', e => {
  e.preventDefault();
  const title = document.getElementById('title').value;
  const due_date = document.getElementById('due_date').value || null;
  const estimated_hours = parseFloat(document.getElementById('estimated_hours').value) || 1;
  const importance = parseInt(document.getElementById('importance').value) || 5;
  const dependencies = (document.getElementById('dependencies').value || '').split(',').map(s=>s.trim()).filter(Boolean);
  tasks.push({title,due_date,estimated_hours,importance,dependencies});
  alert('Task added to local list. Use Analyze to send to server.');
  document.getElementById('taskForm').reset();
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const bulk = document.getElementById('bulk').value.trim();
  let toSend = tasks.slice();
  if(bulk){
    try{
      const parsed = JSON.parse(bulk);
      if(Array.isArray(parsed)) toSend = parsed;
    }catch(e){
      alert('Invalid JSON in bulk input');
      return;
    }
  }
  if(!toSend.length){ alert('No tasks to analyze'); return; }
  // choose strategy weights
  const strat = document.getElementById('strategy').value;
  let weights = null;
  if(strat === 'fast') weights = {urgency:0.2, importance:0.2, effort:0.5, dependency:0.1};
  if(strat === 'impact') weights = {urgency:0.2, importance:0.6, effort:0.1, dependency:0.1};
  if(strat === 'deadline') weights = {urgency:0.7, importance:0.15, effort:0.05, dependency:0.1};
  // send
  try{
    const res = await fetch('/api/tasks/analyze/?weights=' + encodeURIComponent(JSON.stringify(weights || {})), {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(toSend)
    });
    if(!res.ok){ const t = await res.json(); alert('Error: '+ (t.error || JSON.stringify(t))); return; }
    const data = await res.json();
    renderResults(data);
  }catch(e){
    alert('Network error: '+e.message);
  }
});

document.getElementById('suggestBtn').addEventListener('click', async () => {
  try{
    const res = await fetch('/api/tasks/suggest/');
    const data = await res.json();
    if(res.status !== 200){ alert(JSON.stringify(data)); return; }
    renderResults(data.suggestions);
  }catch(e){
    alert('Network error: '+e.message);
  }
});


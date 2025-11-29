from datetime import datetime, date, timedelta
import math

# In-memory cache of last-analyzed tasks (used by GET /suggest/)
last_analyzed_tasks = []

def parse_date(d):
    if isinstance(d, str):
        try:
            return datetime.strptime(d, '%Y-%m-%d').date()
        except Exception:
            return None
    if isinstance(d, date):
        return d
    return None

def detect_cycles(tasks):
    # tasks: list of dicts with 'title' or 'id' and 'dependencies' list (refs by title or id)
    graph = {}
    id_map = {}
    for i, t in enumerate(tasks):
        key = t.get('id') or t.get('title') or str(i)
        id_map[key] = key
        graph[key] = [dep for dep in t.get('dependencies', []) if dep is not None]

    visited = {}
    onstack = {}
    cycles = set()

    def dfs(u):
        visited[u] = True
        onstack[u] = True
        for v in graph.get(u, []):
            if v not in graph:
                continue
            if not visited.get(v):
                dfs(v)
            elif onstack.get(v):
                cycles.add(u)
                cycles.add(v)
        onstack[u] = False

    for node in graph:
        if not visited.get(node):
            dfs(node)
    return cycles

def score_task(task, today=None, weights=None, tasks_by_key=None, blocking_count=0):
    # weights dict: urgency, importance, effort, dependency
    if today is None:
        today = date.today()
    if weights is None:
        weights = {'urgency': 0.4, 'importance': 0.35, 'effort': 0.15, 'dependency': 0.1}

    # normalize inputs and handle missing data
    title = task.get('title', 'Untitled')
    due_date = parse_date(task.get('due_date'))
    importance = task.get('importance') or 5
    estimated = max(0.5, float(task.get('estimated_hours') or 1))

    # Urgency score: based on days left. Past-due => high urgency.
    if due_date is None:
        urgency = 0.2  # unknown due date -> low-medium urgency
    else:
        delta = (due_date - today).days
        if delta < 0:
            urgency = 1.0 + min(1.0, abs(delta)/30.0)  # overdue tasks get >1 (boost)
        else:
            # closer date -> higher urgency. use inverse logistic-like mapping
            urgency = 1.0 / (1.0 + math.log1p(delta+1))
            urgency = min(1.0, urgency * 2.0)

    # Importance normalized 1-10 -> 0..1
    importance_score = max(1, min(10, int(importance))) / 10.0

    # Effort: smaller estimated_hours should be higher quick-win score
    effort_score = 1.0 / (1.0 + math.log1p(estimated))  # decreases with higher time

    # Dependency: if task blocks many others or is depended upon, increase score
    dependency_score = min(1.0, blocking_count / 5.0)

    # Final weighted sum
    raw = (weights['urgency'] * urgency +
           weights['importance'] * importance_score +
           weights['effort'] * effort_score +
           weights['dependency'] * dependency_score)

    # scale to 0-100
    score = round(raw * 100, 2)
    explanation = {
        'urgency_component': round(weights['urgency'] * urgency * 100,2),
        'importance_component': round(weights['importance'] * importance_score * 100,2),
        'effort_component': round(weights['effort'] * effort_score * 100,2),
        'dependency_component': round(weights['dependency'] * dependency_score * 100,2),
        'notes': []
    }
    if due_date and (due_date - today).days < 0:
        explanation['notes'].append('Task is past due — urgent.')
    if task.get('estimated_hours') == 0:
        explanation['notes'].append('Zero estimated hours — treated as very quick task.')
    if blocking_count > 0:
        explanation['notes'].append(f'Blocks {blocking_count} other task(s).')

    return score, explanation

def analyze_tasks(tasks, weights=None, today=None):
    """Main entry point.
    tasks: list of dicts; each dict ideally has 'title' or 'id' and 'dependencies' list.
    Returns list of tasks with added 'score' and 'explanation', sorted descending.
    """
    global last_analyzed_tasks
    if today is None:
        today = date.today()

    # Basic cleanup & keying: create a mapping key -> index
    key_of = {}
    for i, t in enumerate(tasks):
        key = t.get('id') or t.get('title') or str(i)
        key_of[key] = i

    # Count how many tasks depend on each task (blocking count)
    blocking = {k: 0 for k in key_of.keys()}
    for t in tasks:
        deps = t.get('dependencies') or []
        for dep in deps:
            if dep in blocking:
                blocking[dep] += 1

    # detect cycles
    cycles = detect_cycles(tasks)

    results = []
    for i, t in enumerate(tasks):
        key = t.get('id') or t.get('title') or str(i)
        bc = blocking.get(key, 0)
        score, explanation = score_task(t, today=today, weights=weights, tasks_by_key=key_of, blocking_count=bc)
        if key in cycles:
            explanation['notes'].append('Detected circular dependency involving this task.')
            # Penalize slightly if in cycle to force user attention to fix it
            score = round(score * 0.85, 2)
        # attach computed metadata
        out = dict(t)
        out['_key'] = key
        out['score'] = score
        out['explanation'] = explanation
        results.append(out)

    # sort by score desc
    results.sort(key=lambda x: x['score'], reverse=True)

    last_analyzed_tasks = results
    return results


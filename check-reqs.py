import sys
sys.path.insert(0, 'data-model')
import db

reqs = db.list_layer('requirements')
print(f'[INFO] Requirements layer: {len(reqs)} objects')

epics = [r for r in reqs if r.get('type') == 'epic']
stories = [r for r in reqs if r.get('type') == 'story']
print(f'  Epics: {len(epics)}')
print(f'  Stories: {len(stories)}')

done_stories = [s for s in stories if s.get('status') == 'done']
print(f'\n[INFO] Progress:')
print(f'  Done stories: {len(done_stories)}/{len(stories)} ({round(len(done_stories)/len(stories)*100,1) if stories else 0}%)')

print(f'\n[INFO] Sample epics:')
for e in epics[:5]:
    print(f'  {e.get("id")} -- {e.get("title")} ({e.get("status")})')

print(f'\n[INFO] Sample stories (first 5):')
for s in stories[:5]:
    print(f'  {s.get("id")} -- {s.get("title")} ({s.get("status")})')

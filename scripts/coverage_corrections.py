"""Apply sourced, schema-checked dossier display corrections without named rules."""
import hashlib
import json
from pathlib import Path


def apply_configured(coverage, root):
    root=Path(root)
    config=json.loads((root/'config/dossier-corrections.json').read_text())
    if config.get('schemaVersion')!=1 or set(config)!={'schemaVersion','sourceDocument','sourceDocumentSha256','editionCorrections','entryCorrections'}:
        raise ValueError('Invalid dossier correction schema')
    raw=(root/config['sourceDocument']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['sourceDocumentSha256']:
        raise ValueError('Dossier correction evidence changed; review the configuration')
    evidence=json.loads(raw)
    companies={c['id']:c for c in coverage['companies']}
    for rule in config['editionCorrections']:
        correction=evidence[rule['sourceKey']]
        company=companies[correction['dossierId']]
        work=next(w for w in company['relatedGames'] if w['id']==correction['workId'])
        old=work['editionCredits']
        if len(old)!=1 or old[0]['publisher']!=correction['oldEditionPublisher'] or old[0]['year']!=correction['year'] or old[0]['platform']!=correction['platform']:
            raise ValueError('Dossier correction target baseline changed')
        work['editionCredits']=[{**old[0],'publisher':correction['newEditionPublisher'],'source':correction['source'],'reason':rule['reason']}]
        work['notes']=rule['notes']
        for entry in company['entries']:
            if entry.get('title')==work['title']:
                if correction['workId'] not in entry['relatedIds']:
                    raise ValueError('Dossier correction identity mismatch')
                entry.update(status=rule['entryStatus'],reason=work['notes'],source=correction['source'])
            elif entry.get('title')==rule['companionTitle']:
                entry['reason']=entry['reason'].replace(rule['removeText'],'').replace(rule['replaceFrom'],rule['replaceTo'])
    for rule in config['entryCorrections']:
        entry=next(e for e in companies[rule['dossierId']]['entries'] if e['title']==rule['title'])
        entry['reason']=rule['reason']
        if rule.get('sourceRef'):
            ref=rule['sourceRef']
            entry['source']=next(r for r in evidence['records'] if r['recordId']==ref['recordId'])['sources'][ref['index']]['url']
    return coverage

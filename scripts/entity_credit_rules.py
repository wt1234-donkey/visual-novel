"""Apply scoped historical credit facts without inferring relationships by name."""
from historical_rules import resolve_evidence

def apply_credit_rules(rules,phase,*,companies,works,releases,contents,release_entities,credit,credits):
    for rule in rules['creditRules'][phase]:
        if rule.get('requiresDossier') and rule['requiresDossier'] not in companies:
            continue
        scope=rule['scope'];selection=rule['targets']
        if selection['kind']=='dossierWorks':
            targets=[works[wid] for wid in companies[selection['dossier']]['workIds'] if wid not in selection.get('exclude',[])]
        elif selection['kind']=='ids':
            mapping=works if scope=='work' else {r['id']:r for r in (releases if scope=='release' else contents)}
            targets=[mapping[wid] for wid in selection['ids']]
        else:
            targets=[r for r in (releases if scope=='release' else contents) if r['workId'] in selection['workIds'] and
                     ('firstYear' not in selection or r['firstYear']==selection['firstYear']) and
                     ('publisherEntity' not in selection or selection['publisherEntity'] in release_entities(r))]
        for target in targets:
            wid=target['id'] if scope=='work' else target['workId']
            if rule.get('requiresOriginalRelease'):
                assert any(r['workId']==wid and r['contentRelation']=='original' for r in releases)
            source=rule['source']
            if isinstance(source,dict) and set(source)=={'workSource'}:
                source=works[wid]['source']
            elif isinstance(source,dict) and set(source)=={'targetSources'}:
                source=source['targetSources'][target['id']]
            else:
                source=resolve_evidence(source,companies)
            options={'status':rule['status'],'note':rule['note']}
            if scope!='work':options['work_id']=wid
            if 'raw' in rule:options['raw']=rule['raw']
            credit(rule['entityId'],scope,target['id'],rule['role'],source,**options)
            if 'review' in rule:
                credits[-1].update(reviewId=rule['review']['id'].format(workId=wid),reviewRecord=rule['review']['record'])

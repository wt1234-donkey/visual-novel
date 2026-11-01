"""Hold unresolved original-year contradictions before reserving identities."""
import re


def hold_date_conflict(vndb_year, ctx, item, source_id, names, next_date):
    match = re.match(r'^(\d{4})(?:-|$)', str(next_date or ''))
    next_year = int(match.group(1)) if match else None
    canonical_year = vndb_year(item) if ctx['kind'] == 'nextmoe' else None
    if next_year and canonical_year and canonical_year > next_year:
        ctx['counts']['source-date-conflict-held'] += 1
        ctx['held'].append({
            'sourceId': str(source_id), 'vndbId': item['id'],
            'title': names[0] if names else '',
            'sourceReleased': item.get('released'),
            'nextmoeSourceReleased': next_date,
            'reason': 'VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review.'})
        return True
    return False


def reviewed_add_fresh(original, vndb_year, ctx, item, source_id, names,
                       index, refs, extra=None):
    if hold_date_conflict(vndb_year, ctx, item, source_id, names,
                          (extra or {}).get('nextmoeSourceReleased')):
        return None
    return original(ctx, item, source_id, names, index, refs, extra)

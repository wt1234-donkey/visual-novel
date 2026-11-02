import datetime as dt
import sys
import unittest
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import ifdb_archive_identity as f
import import_basic_r60_r61_20261102 as intake


class IFDBIdentityTests(unittest.TestCase):
    def game(self,tuid='aaaaaaaaaaaaaaaa',**kw):
        return {'id':tuid,'title':'New story','author':'Author','published':'1993-01-01 00:00:00',
            'system':'Inform','language':'en','flags':0,'website':None,'tags':'',**kw}

    def data(self,*games):
        return {'games':list(games),'gamefwds':[],'ifids':[],'gamexrefs':[],'gamelinks':[]}

    def test_sql_literals_and_inert_code(self):
        values=r"('It\'s \\ fine',NULL,-3,'a\nb','$(do not run)'),('next','x',0,'','');"
        rows=list(f.sql_rows(values))
        self.assertEqual(rows[0],["It's \\ fine",None,-3,'a\nb','$(do not run)'])
        self.assertEqual(rows[1],['next','x',0,'',''])
        with self.assertRaises(ValueError): list(f.sql_rows('(NOW());'))

    def test_published_not_created_and_future_hold(self):
        d=self.data(self.game(created='2026-01-01'),self.game('bbbbbbbbbbbbbbbb',published='2027-01-01'))
        rows,counts=f.prepare(d,dt.date(2026,11,2))
        self.assertEqual(rows[0]['firstYear'],1993)
        self.assertEqual(counts['outside-original-year-window'],1)

    def test_missing_published_is_not_creation_year(self):
        rows,counts=f.prepare(self.data(self.game(published=None,created='1993-01-01')),dt.date(2026,11,2))
        self.assertEqual(rows,[])
        self.assertEqual(counts['missing-or-invalid-published-date'],1)

    def test_redirect_alias_and_ifid(self):
        d=self.data(self.game(),self.game('bbbbbbbbbbbbbbbb',title='Prior title'))
        d['gamefwds']=[{'gameid':'bbbbbbbbbbbbbbbb','fwdgameid':'aaaaaaaaaaaaaaaa'}]
        d['ifids']=[{'gameid':'bbbbbbbbbbbbbbbb','ifid':'UUID-ABC'}]
        rows,_=f.prepare(d,dt.date(2026,11,2))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['aliases'],['Prior title'])
        self.assertIn('ifid:uuid-abc',rows[0]['sourceRefs'])
        self.assertIn('ifdb:bbbbbbbbbbbbbbbb',rows[0]['sourceRefs'])
        with self.assertRaises(ValueError): f.canonical_id('a',{'a':'b','b':'a'})

    def test_ports_translations_remakes_held_sequel_allowed(self):
        for relation in (2,4,7,5):
            d=self.data(self.game())
            d['gamexrefs']=[{'fromid':'aaaaaaaaaaaaaaaa','toid':'bbbbbbbbbbbbbbbb','reftype':relation}]
            rows,_=f.prepare(d,dt.date(2026,11,2))
            self.assertEqual(len(rows),int(relation==5))

    def test_ifid_collision_with_ineligible_identity(self):
        d=self.data(self.game(),self.game('bbbbbbbbbbbbbbbb',published=None))
        d['ifids']=[{'gameid':'aaaaaaaaaaaaaaaa','ifid':'ABC'},{'gameid':'bbbbbbbbbbbbbbbb','ifid':'abc'}]
        rows,counts=f.prepare(d,dt.date(2026,11,2))
        self.assertEqual(rows,[])
        self.assertEqual(counts['shared-ifid-held'],1)

    def test_case_insensitive_ifid_reuse_and_name_year_hold(self):
        rows,_=f.prepare(self.data(self.game(),self.game('bbbbbbbbbbbbbbbb',title='Another story')),dt.date(2026,11,2))
        rows[0]['sourceRefs'].append('ifid:UUID')
        index=defaultdict(set,{'another story':{('old',1994,'complete')}})
        refs=defaultdict(set,{'ifid:uuid':{'existing'}})
        selected,review=f.choose(rows,0,index,refs,str.casefold,'batch')
        self.assertEqual(selected,[])
        with self.assertRaisesRegex(RuntimeError,'Only 0'):
            f.choose(rows,1,index,refs,str.casefold,'batch')
        self.assertNotIn('ifdb:bbbbbbbbbbbbbbbb',refs)

    def test_selection_reserves_aliases_and_refs(self):
        rows,_=f.prepare(self.data(self.game()),dt.date(2026,11,2))
        rows[0]['aliases']=['Known alias']
        index,refs=defaultdict(set),defaultdict(set)
        selected,review=f.choose(rows,1,index,refs,str.casefold,'batch')
        self.assertEqual(len(selected),1)
        self.assertTrue(index['known alias'])
        self.assertEqual(refs['ifdb:aaaaaaaaaaaaaaaa'],{'ifdb-aaaaaaaaaaaaaaaa'})
        self.assertEqual(review['scanned'],1)

    def test_decade_author_round_robin(self):
        rows=[{'tuid':str(i),'firstYear':y,'author':a} for i,(y,a) in enumerate([(1980,'a'),(1980,'a'),(1980,'b'),(2020,'a')])]
        order=list(f.diverse_order(rows))
        self.assertEqual([r['firstYear'] for r in order[:2]],[1980,2020])
        self.assertEqual(order[2]['author'],'b')

    def test_vndb_link_held(self):
        d=self.data(self.game(website='https://vndb.org/v123'))
        rows,counts=f.prepare(d,dt.date(2026,11,2))
        self.assertEqual(rows,[])
        self.assertEqual(counts['cross-vndb-link-held'],1)

    def test_next_selection_keeps_queue_priority_and_quota(self):
        def row(i,origin):
            return {'work':{'id':str(i),'firstYear':2000},'developers':[],'intakeOrigin':origin}
        pending=[row(i,'deferred') for i in range(27)]
        fresh=[row(i,'live') for i in range(27,527)]
        chosen,remaining=intake.select_next({'pending':pending,'fresh':fresh},{'works':[]})
        self.assertEqual(len(chosen),300)
        self.assertEqual(chosen[:27],pending)
        self.assertEqual(len(remaining),227)
        self.assertFalse({r['work']['id'] for r in chosen}&{r['work']['id'] for r in remaining})

if __name__=='__main__': unittest.main()

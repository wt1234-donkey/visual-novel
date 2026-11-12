"""Confirm actual deployed ancestry, rather than equating build success to publication."""
import argparse
import json
import time
import urllib.request

def contains(deployment,commit):
    return deployment.get('revision')==commit or commit in deployment.get('ancestors',[])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('commit');parser.add_argument('--timeout',type=int,default=1200);args=parser.parse_args()
    started=time.monotonic()
    while time.monotonic()-started<args.timeout:
        try:
            request=urllib.request.Request('https://wt1234-donkey.github.io/visual-novel/deployment.json?verify='+str(time.time_ns()),headers={'Cache-Control':'no-cache'})
            with urllib.request.urlopen(request,timeout=30) as response:deployment=json.load(response)
            if contains(deployment,args.commit):print('Publication verified: '+deployment['revision']);return
        except (OSError,ValueError):pass
        time.sleep(10)
    raise SystemExit('Data was saved, but its online publication could not be confirmed')
if __name__=='__main__':main()

import {installReleaseRecovery} from './src/features/release-recovery.mjs';
import {installPublicationStatus} from './src/features/publication-status.mjs';
if(typeof document!=='undefined'){
 const install=()=>{installReleaseRecovery();installPublicationStatus();};
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
}

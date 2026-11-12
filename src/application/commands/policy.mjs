export function saveMode(policy){
 if(policy===undefined)return 'legacy';
 if(!policy||policy.schemaVersion!==1||!['legacy','trusted'].includes(policy.mode))throw Error('保存策略格式无效，拒绝隐式回退');
 return policy.mode;
}

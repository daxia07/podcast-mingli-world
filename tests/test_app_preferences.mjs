import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';
const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const app=await readFile(join(root,'site/app.js'),'utf8');
const shelf=await readFile(join(root,'site/js/shelf.js'),'utf8');

function harness(store=new Map()) {
  const nodes=new Map(),events=new Map();
  function node(id) {
    if(!nodes.has(id))nodes.set(id,{id,innerHTML:'',textContent:'',hidden:false,dataset:{},style:{},attributes:{},children:[],
      classList:{add(){},remove(){},toggle(){}},addEventListener(){},removeEventListener(){},querySelectorAll(){return []},querySelector(){return null},
      setAttribute(k,v){this.attributes[k]=v},currentTime:0,duration:600,defaultPlaybackRate:1,playbackRate:1,
      insertAdjacentHTML(_,s){this.innerHTML+=s},
      load(){this.playbackRate=this.defaultPlaybackRate},play(){return Promise.resolve()},pause(){}});
    return nodes.get(id);
  }
  const localStorage={getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v)};
  const document={getElementById:node,querySelectorAll:()=>[],querySelector:()=>null,addEventListener(){}};
  const window={addEventListener:(k,f)=>events.set(k,f)};
  const context={window,document,localStorage,navigator:{},console,URLSearchParams,setTimeout:()=>0,clearTimeout(){}};
  vm.createContext(context);vm.runInContext(shelf,context);
  // Exercise the real app's functions and registered handlers. Only stop the
  // network boot and expose closure state in this test copy of the source.
  const exposed=app.replace('// ——— boot ———',`window.TestApp = {
    setData: function(e,p){ episodes=e; playlists=p; adoptShowsFromManifest(); },
    episodesForShow: episodesForShow,
    meta: showMeta,
    renderHome: renderHome,
    openShow: openShow,
    openLinkedEpisode: openLinkedEpisode,
    renderShelved: renderShelved,
    order: function(){return SHOW_ORDER.slice();}
  }; return; // ——— boot ———`);
  vm.runInContext(exposed,context);
  return {app:window.TestApp,Shelf:window.Shelf,node,events,store};
}
function catalogue(){return {
  episodes:[
    {id:1,playlist:'history',archived:true,title:'Old first',file_url:'/episodes/old-first.mp3?v=keep'},
    {id:2,playlist:'history',archived:true,title:'Old second',file_url:'/episodes/old-second.mp3?v=keep'},
    {id:3,playlist:'history',archived:true,title:'Tagged fallback',file_url:'/episodes/tagged.mp3'},
    {id:99,playlist:'interviews',title:'Interview prep',file_url:'/episodes/interview.mp3?v=keep'}
  ],
  playlists:[{id:'history',title:'Preserved history',mono:'PH',archived:true,featured:true,order:1,episode_ids:[2,1]},
             {id:'interviews',title:'Interview prep',mono:'IP',featured:true,order:0,episode_ids:[99]}]
};}

test('restoring an archived show recovers ordered and tag-only episodes without mutating the catalogue',()=>{
  const h=harness(),c=catalogue(),before=JSON.stringify(c);h.app.setData(c.episodes,c.playlists);
  assert.equal(h.app.episodesForShow('history').length,0);
  h.Shelf.setShowRestored('history',true);
  assert.equal(h.app.episodesForShow('history').map(e=>e.id).join(','),'2,1,3');
  h.Shelf.setShelved(2,true);
  assert.equal(h.app.episodesForShow('history').map(e=>e.id).join(','),'1,3');
  assert.equal(h.app.episodesForShow('interviews')[0].file_url,'/episodes/interview.mp3?v=keep');
  h.Shelf.setShowRestored('history',false);
  assert.equal(h.app.episodesForShow('history').length,0);
  assert.equal(JSON.stringify(c),before,'archive flags, identities and URLs are untouched');
});

test('the restore event updates show metadata and browsing views; undo hides it again',()=>{
  const h=harness(),c=catalogue();h.app.setData(c.episodes,c.playlists);
  assert.equal(h.app.meta('history').mono,'PH');
  h.Shelf.setShowRestored('history',true);h.events.get('shelf:change')();
  assert.ok(h.node('libraryList').innerHTML.includes('Preserved history'));
  assert.ok(h.node('showRow').innerHTML.includes('Preserved history'));
  assert.ok(h.app.order().includes('history'));
  h.Shelf.setShowRestored('history',false);h.events.get('shelf:change')();
  assert.ok(!h.node('libraryList').innerHTML.includes('Preserved history'));
  assert.ok(h.node('libraryList').innerHTML.includes('Interview prep'));
});

test('shelving every System Design episode does not make the home fallback resurrect it',()=>{
  const h=harness(),e={id:7,playlist:'system-design',title:'Design',file_url:'/episodes/design.mp3'};
  h.app.setData([e],[{id:'system-design',title:'System Design',episode_ids:[7],featured:true}]);
  h.Shelf.setShelved(7,true);h.app.renderHome();
  assert.ok(!h.node('showRow').innerHTML.includes('System Design'));
});

test('1.1x preference survives reload and media load, with matching accessible label',()=>{
  const store=new Map(),h=harness(store);h.node('btnSpeed').onclick();
  assert.equal(h.node('audio').playbackRate,1.1);assert.equal(store.get('pod_speed'),'1.1');
  const reloaded=harness(store);reloaded.node('audio').load();
  assert.equal(reloaded.node('audio').playbackRate,1.1);
  assert.equal(reloaded.node('btnSpeed').textContent,'1.1×');
  assert.equal(reloaded.node('btnSpeed').attributes['aria-label'],'Playback speed 1.1 times');
});

test('invalid saved speed and unavailable storage fall back to normal speed',()=>{
  for(const value of ['99','-1','"1.1"','{}','not-json']) {
    const h=harness(new Map([['pod_speed',value]]));assert.equal(h.node('audio').playbackRate,1);
  }
  const broken={get(){throw new Error('storage blocked')},set(){throw new Error('storage blocked')}};
  const h=harness(broken);assert.equal(h.node('audio').playbackRate,1);assert.doesNotThrow(()=>h.node('btnSpeed').onclick());
});

test('draft opening is readable in Home and Library without fake playable episode identities',()=>{
  const h=harness(),c=catalogue();
  c.playlists.push({id:'novel',title:'开篇三章',mono:'回声',featured:true,episode_ids:[],
    draft_chapters:[1,2,3].map(n=>({slug:'opening-'+n,title:'第'+n+'章',status:'text-ready-audio-pending',reader_url:'/novel/opening-'+n+'.html'}))});
  h.app.setData(c.episodes,c.playlists);h.app.renderHome();
  assert.equal((h.node('showRow').innerHTML.match(/data-show="novel"/g)||[]).length,1,'featured show is not duplicated');
  assert.ok(h.node('showRow').innerHTML.includes('3 章原文'));
  h.events.get('shelf:change')();assert.ok(h.node('libraryList').innerHTML.includes('开篇三章'));
  h.app.openShow('novel');assert.equal(h.node('showPlayAll').disabled,true);assert.equal(h.node('showQueueAll').disabled,true);
  assert.equal((h.node('showEpisodes').innerHTML.match(/draft-chapter/g)||[]).length,3);
  assert.ok(!h.node('showEpisodes').innerHTML.includes('data-play='));
  assert.equal(h.app.episodesForShow('novel').length,0);
});

test('archived aliases remain in catalogue and can be restored with original URL and ID',()=>{
  const h=harness(),c=catalogue(),before=JSON.stringify(c);
  h.Shelf.setAliases({'99':100});h.app.setData(c.episodes,c.playlists);
  assert.equal(h.app.episodesForShow('interviews').length,0);
  h.app.renderShelved(h.node('libraryList'));assert.ok(h.node('libraryList').innerHTML.includes('data-alias="99"'));
  h.Shelf.setAliasRestored(99,true);h.events.get('shelf:change')();
  assert.equal(h.app.episodesForShow('interviews')[0].id,99);
  assert.equal(h.app.episodesForShow('interviews')[0].file_url,c.episodes[3].file_url);
  h.Shelf.setAliasRestored(99,false);assert.equal(h.app.episodesForShow('interviews').length,0);
  assert.equal(JSON.stringify(c),before);
});

test('episode links open the correct collection without playing or restoring hidden records',()=>{
  const h=harness(),c=catalogue();h.app.setData(c.episodes,c.playlists);
  c.episodes[3].reader_url='/novel/chapter-one.html';
  assert.equal(h.app.openLinkedEpisode('?episode=99'),true);
  assert.equal(h.node('showName').textContent,'Interview prep');
  assert.ok(h.node('showEpisodes').innerHTML.includes('href="/novel/chapter-one.html"'));
  assert.equal(h.node('audio').src,undefined);assert.equal(h.store.get('pod_progress'),undefined);
  for(const query of ['?episode=1','?episode=-99','?episode=99<script>','?episode=1234'])
    assert.equal(h.app.openLinkedEpisode(query),false);
});

/* LinkCar — interface sem frameworks, integrada às APIs Flask existentes. */
'use strict';
const $ = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>Array.from(root.querySelectorAll(s));
const page = document.body.dataset.page;
const money = v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(Number(v)||0);
const esc = v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
let toastTimer;
function aviso(msg,error=false){const t=$('#toast');t.textContent=msg;t.className='toast show'+(error?' error':'');clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.className='toast',4500)}
async function api(path,{method='GET',body}={}){
  const options={method,credentials:'same-origin',headers:{'Accept':'application/json'}};
  if(body!==undefined){options.headers['Content-Type']='application/json';options.body=JSON.stringify(body)}
  let response;
  try{response=await fetch(path,options)}catch(e){throw new Error('Não foi possível conectar ao servidor Flask. Confira se ele está ligado.')}
  let content={};try{content=await response.json()}catch{}
  if(!response.ok){const err=new Error(content.erro||content.mensagem||`Erro HTTP ${response.status}`);err.status=response.status;throw err}
  return content;
}
function formObj(form){return Object.fromEntries(new FormData(form))}
function go(path){location.href=path}
function invalidMessage(e){aviso(e.message||'Não foi possível concluir.',true)}
// Fotografias de modelos reais em alta resolução, Wikimedia Commons.
// Se não houver correspondência confiável, mostramos um SVG neutro (sem carro inventado).
const FOTO_ORIGEM = {
  'honda-civic-2012.jpg': 'https://upload.wikimedia.org/wikipedia/commons/0/0d/2012_Honda_Civic_EX_sedan.jpg',
  'fiat-strada-2015.jpg': 'https://upload.wikimedia.org/wikipedia/commons/5/50/Fiat_Strada_1.4_Trekking_Crew_Cab_2015_%2816887528745%29.jpg',
  'honda-civic-2016.jpg': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Honda_Civic_2016.jpg',
  'honda-civic-hatch-2016.jpg': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Honda_Civic_5d_-_prz%C3%B3d_%28MSP16%29.jpg',
  'jeep-compass-2018.jpg': 'https://upload.wikimedia.org/wikipedia/commons/9/96/2018_Jeep_Compass_Latitude_2.4L_front_4.20.19.jpg',
  'volkswagen-polo-2019.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Volkswagen_Polo_2019.jpg',
  'ford-mustang-2018.jpg': 'https://upload.wikimedia.org/wikipedia/commons/5/5d/2018_Ford_Mustang_GT_5.0_Front.jpg',
  'fiat-doblo-2017.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/35/2017_Fiat_Doblo_%28263_Series_II%29_SWB_van_%282018-09-03%29_01.jpg',
};
const FOTO_BASE = '/static/img/fotos/';
const FOTO_SEM_MODELO = '/static/img/fotos/sem-foto.svg';
function normalizaModelo(txt){return String(txt??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
function fotoDoModelo(v){
  const marca=normalizaModelo(v.marca), modelo=normalizaModelo(v.modelo);
  const ano=Number(v.ano||0);
  // Bloqueia anúncios de teste: não são modelos reais.
  if(/teste|rlx/.test(marca+' '+modelo))return null;
  if(marca.includes('honda') && modelo.includes('civic')){
    if(modelo.includes('exs') && (!ano || ano===2012))return 'honda-civic-2012.jpg';
    if(ano>=2011 && ano<=2015)return 'honda-civic-2012.jpg';
    if(ano>=2016 && ano<=2017){
      if(normalizaModelo(v.carroceria).includes('hatch'))return 'honda-civic-hatch-2016.jpg';
      return 'honda-civic-2016.jpg';
    }
    // Ano desconhecido: não supor qual geração foi anunciada.
    return null;
  }
  if(marca.includes('fiat') && modelo.includes('strada') && ano>=2013 && ano<=2017)return 'fiat-strada-2015.jpg';
  if(marca.includes('jeep') && modelo.includes('compass') && ano>=2017 && ano<=2020)return 'jeep-compass-2018.jpg';
  if((marca.includes('vw')||marca.includes('volkswagen')) && modelo.includes('polo') && ano>=2018 && ano<=2021)return 'volkswagen-polo-2019.jpg';
  if(marca.includes('ford') && modelo.includes('mustang') && ano>=2018 && ano<=2020)return 'ford-mustang-2018.jpg';
  if(marca.includes('fiat') && modelo.includes('doblo') && ano>=2016 && ano<=2019)return 'fiat-doblo-2017.jpg';
  return null;
}
function imagemDoVeiculo(v){
  const nome=fotoDoModelo(v);
  if(!nome)return {src:FOTO_SEM_MODELO, backup:'', desc:'Sem foto cadastrada para este anúncio', possui:false};
  return {src:FOTO_BASE+nome,backup:FOTO_ORIGEM[nome],desc:`Fotografia ilustrativa de ${String(v.marca)} ${String(v.modelo)}; versão e cor podem variar`,possui:true};
}
// Tenta primeiro a foto local; se não foi baixada ainda, usa a imagem de origem.
// Evita imagens quebradas quando offline ou se a fonte estiver temporariamente indisponível.
document.addEventListener('error',event=>{
  const img=event.target;
  if(!(img instanceof HTMLImageElement)||!img.matches('.model-photo, .category-photo'))return;
  const remoto=img.dataset.backup;
  if(remoto){img.dataset.backup='';img.src=remoto;return;}
  if(!img.src.endsWith('/sem-foto.svg'))img.src=FOTO_SEM_MODELO;
},true);
function vehicleCard(v,{favorite=false,score=null,details=null}={}){
  const id=Number(v.id_veiculo);
  const foto=imagemDoVeiculo(v);
  return `<article class="vehicle-card"><div class="vehicle-picture"><img class="model-photo" src="${foto.src}" data-backup="${foto.backup}" loading="lazy" decoding="async" alt="${esc(foto.desc)}"><span class="badge">${score!==null?`${Number(score)}% Match`:'Disponível'}</span></div><div class="vehicle-content"><h3>${esc(v.marca)} ${esc(v.modelo)}</h3><p class="vehicle-meta">${esc(v.ano||'')} · ${esc(v.carroceria||v.combustivel||'')} · ${esc(v.cor||'')}</p><div class="vehicle-price">${money(v.preco)}</div>${details?`<p class="match-explanation">${esc(details)}</p>`:''}<div class="vehicle-actions"><button type="button" class="btn btn-outline" data-info="${id}">Ver informações</button><button class="heart ${favorite?'active':''}" type="button" data-favorito="${id}" data-mode="${favorite?'remove':'add'}" aria-label="${favorite?'Remover dos favoritos':'Adicionar aos favoritos'}">${favorite?'♥':'♡'}</button></div></div></article>`
}
function showInfo(v){const fields=[['Marca',v.marca],['Modelo',v.modelo],['Ano',v.ano],['Preço',money(v.preco)],['Quilometragem',(v.quilometragem??'—')+' km'],['Combustível',v.combustivel],['Câmbio',v.cambio],['Carroceria',v.carroceria],['Cor',v.cor],['Motor',v.motor],['Espaço interno',v.espaco_interno],['Estilo',v.estilo_design],['Descrição',v.descricao]];alert(fields.map(([k,val])=>`${k}: ${val||'—'}`).join('\n'))}
let knownCars=[];
function bindVehicleArea(root=document){root.addEventListener('click',async evt=>{
  const info=evt.target.closest('[data-info]');if(info){const v=knownCars.find(v=>Number(v.id_veiculo)===Number(info.dataset.info));if(v)showInfo(v);return}
  const fav=evt.target.closest('[data-favorito]');if(!fav)return;
  const id=Number(fav.dataset.favorito);try{
    if(fav.dataset.mode==='add'){await api('/api/favoritos',{method:'POST',body:{id_veiculo:id}});aviso('Adicionado aos favoritos!');fav.dataset.mode='remove';fav.classList.add('active');fav.textContent='♥'}
    else{await api(`/api/favoritos/${id}`,{method:'DELETE'});aviso('Removido dos favoritos!');fav.dataset.mode='add';fav.classList.remove('active');fav.textContent='♡';if(page==='favoritos')loadFavoritos()}
  }catch(e){invalidMessage(e)}
})}
async function sessionHeader(){const box=$('#account');try{const data=await api('/api/sessao');const u=data.usuario;box.innerHTML=`<span class="name">Olá, ${esc(u.nome.split(' ')[0])}</span><button type="button" id="logout" class="btn btn-outline btn-small">Sair</button>`;$('#logout').addEventListener('click',async()=>{try{await api('/api/logout',{method:'POST'});go('/login')}catch(e){invalidMessage(e)}});if(!u.permissoes.includes('cadastrar_veiculos')){$('[data-nav="anunciante"]').style.display='none'}}catch(e){$('[data-nav="anunciante"]').style.display='none'}}
async function loginInit(){const form=$('#form-login');form.addEventListener('submit',async e=>{e.preventDefault();const submit=$('button[type="submit"]',form);submit.disabled=true;try{const data=await api('/api/login',{method:'POST',body:formObj(form)});aviso('Login realizado!');const next=new URLSearchParams(location.search).get('proximo');if(next&&next.startsWith('/')&&!next.startsWith('//'))go(next);else go(data.perfil==='Anunciante'?'/anunciante':'/catalogo')}catch(err){invalidMessage(err)}finally{submit.disabled=false}})}
async function cadastroInit(){const form=$('#form-cadastro');form.addEventListener('submit',async e=>{e.preventDefault();const d=formObj(form);if(d.senha!==d.confirmar){aviso('As senhas não coincidem.',true);return}delete d.confirmar;const b=$('button[type="submit"]',form);b.disabled=true;try{await api('/api/cadastro',{method:'POST',body:d});aviso('Cadastro realizado! Faça login.');setTimeout(()=>go('/login'),950)}catch(err){invalidMessage(err)}finally{b.disabled=false}})}
function recoveryInit(){const form=$('#form-recuperacao');form.addEventListener('submit',async e=>{e.preventDefault();const b=$('button[type="submit"]',form);b.disabled=true;try{const d=await api('/api/recuperar-senha',{method:'POST',body:formObj(form)});aviso(d.mensagem||'Se o e-mail estiver cadastrado, você receberá instruções.')}catch(err){invalidMessage(err)}finally{b.disabled=false}})}
async function loadCars(){const result=await api('/api/veiculos');return result.veiculos||[]}
async function homeInit(){const list=$('#home-cars');try{const cars=await loadCars();knownCars=cars;list.innerHTML=cars.length?cars.slice(0,4).map(v=>vehicleCard(v)).join(''):'<div class="empty">Ainda não existem anúncios ativos.</div>'}catch(e){list.innerHTML='<div class="empty">Entre na sua conta para visualizar os veículos disponíveis. <a class="text-link" href="/login">Entrar ↗</a></div>'}}
async function catalogInit(){const root=$('#catalog-cars');try{knownCars=await loadCars();let f;const render=()=>{const search=$('#busca').value.trim().toLowerCase(),max=Number($('#max-preco').value),body=$('#filtro-carroceria').value.toLowerCase();f=knownCars.filter(v=>(`${v.marca} ${v.modelo}`).toLowerCase().includes(search)&&(!max||Number(v.preco)<=max)&&(!body||(body==='esportivo'?(v.estilo_design||'').toLowerCase()===body:(v.carroceria||'').toLowerCase()===body)));$('#result-count').textContent=`${f.length} veículo(s) encontrado(s)`;root.innerHTML=f.length?f.map(v=>vehicleCard(v)).join(''):'<div class="empty">Nenhum veículo encontrado com esses filtros.</div>'};const urlCategoria=new URLSearchParams(location.search).get('carroceria');if(urlCategoria){const sel=$('#filtro-carroceria');if([...sel.options].some(o=>o.value===urlCategoria))sel.value=urlCategoria;}['#busca','#max-preco','#filtro-carroceria'].forEach(s=>$(s).addEventListener('input',render));$('#limpar-filtros').addEventListener('click',()=>{$('#busca').value='';$('#max-preco').value='';$('#filtro-carroceria').value='';render()});render()}catch(e){root.innerHTML='<div class="empty">Não foi possível carregar os anúncios.</div>';invalidMessage(e)}}
async function favoritesInit(){await loadFavoritos()}
async function loadFavoritos(){const target=$('#favoritos-lista');try{const data=await api('/api/favoritos');const detalhes=await loadCars().catch(()=>[]);const porId=new Map(detalhes.map(v=>[Number(v.id_veiculo),v]));knownCars=(data.favoritos||[]).map(v=>({...porId.get(Number(v.id_veiculo)),...v}));target.innerHTML=knownCars.length?knownCars.map(v=>vehicleCard(v,{favorite:true})).join(''):'<div class="empty">Você ainda não tem favoritos. <a class="text-link" href="/catalogo">Explorar veículos ↗</a></div>'}catch(e){invalidMessage(e)}}
async function loadResources(select){if(!select)return;const data=await api('/api/recursos');select.innerHTML=(data.recursos||[]).map(x=>`<option value="${Number(x.id_recurso)}">${esc(x.nome_recurso)}</option>`).join('');return data.recursos||[]}
async function matchInit(){
  const form=$('#form-match');
  const box=$('#match-recursos');
  const count=$('#match-recursos-contagem');
  const selected=new Set();
  const syncCount=()=>{
    const n=selected.size;
    count.textContent=n?`${n} recurso${n===1?' selecionado':'s selecionados'}`:'Nenhum recurso selecionado';
    $('#limpar-match-recursos').disabled=n===0;
  };
  try{
    const data=await api('/api/recursos');
    const resources=data.recursos||[];
    box.innerHTML=resources.length?resources.map(x=>`<button type="button" class="match-chip" data-match-recurso="${esc(x.nome_recurso)}" aria-pressed="false">${esc(x.nome_recurso)}</button>`).join(''):'<span class="muted small">Nenhum recurso cadastrado.</span>';
  }catch(err){box.innerHTML='<span class="muted small">Não foi possível carregar os recursos.</span>';invalidMessage(err)}
  syncCount();
  box.addEventListener('click',e=>{
    const button=e.target.closest('button[data-match-recurso]');
    if(!button)return;
    const name=button.dataset.matchRecurso;
    if(selected.has(name))selected.delete(name);else selected.add(name);
    const active=selected.has(name);
    button.classList.toggle('selected',active);
    button.setAttribute('aria-pressed',String(active));
    syncCount();
  });
  $('#limpar-match-recursos').addEventListener('click',()=>{
    selected.clear();
    $$('.match-chip',box).forEach(b=>{b.classList.remove('selected');b.setAttribute('aria-pressed','false')});
    syncCount();
  });
  form.addEventListener('submit',async e=>{
    e.preventDefault();
    const payload={};
    for(const [k,v] of new FormData(form)){
      if(String(v).trim())payload[k]=k==='preco'?Number(v):String(v).trim();
    }
    payload.recursos=Array.from(selected);
    const out=$('#match-resultados');
    out.innerHTML='<div class="empty">Calculando compatibilidade…</div>';
    try{
      const d=await api('/api/match',{method:'POST',body:payload});
      $('#match-intro').style.display='none';
      knownCars=d.resultados||[];
      out.innerHTML=knownCars.length?knownCars.map(v=>vehicleCard(v,{score:v.porcentagem??v.compatibilidade??0,details:(v.atendidos||[]).slice(0,3).join(' • ')})).join(''):'<div class="empty">Nenhum veículo combina com os filtros atuais. Experimente ampliar suas preferências.</div>';
    }catch(err){invalidMessage(err);out.innerHTML=''}
  });
}
async function advertiserInit(){const root=$('#meus-veiculos');try{const data=await api('/api/anunciante/meus-veiculos');const cars=data.veiculos||[];$('#stat-total').textContent=cars.length;$('#stat-media').textContent=cars.length?money(cars.reduce((sum,v)=>sum+Number(v.preco),0)/cars.length):money(0);root.innerHTML=cars.length?cars.map(v=>`<div class="listing-item"><div><strong>${esc(v.marca)} ${esc(v.modelo)}</strong><small>${esc(v.ano)} · ${money(v.preco)} · ID ${Number(v.id_veiculo)}</small></div><div class="listing-actions"><a class="btn btn-outline btn-small" href="/anunciante/editar/${Number(v.id_veiculo)}">Editar</a><button class="btn btn-danger btn-small" data-excluir="${Number(v.id_veiculo)}">Desativar</button></div></div>`).join(''):'<div class="empty">Você ainda não possui anúncios ativos. <a class="text-link" href="/anunciante/novo">Publicar primeiro veículo ↗</a></div>';root.onclick=async e=>{const btn=e.target.closest('[data-excluir]');if(!btn)return;const id=Number(btn.dataset.excluir);if(!confirm('Desativar este anúncio? O registro continuará salvo no banco.'))return;try{await api(`/api/veiculos/${id}`,{method:'DELETE'});aviso('Anúncio desativado!');advertiserInit()}catch(err){invalidMessage(err)}}}catch(e){root.innerHTML='<div class="empty">Não foi possível carregar seus anúncios.</div>';invalidMessage(e)}}
async function vehicleFormInit(){
 const form=$('#form-veiculo'),mode=document.body.dataset.modo,recordId=Number(document.body.dataset.id||0);
 const box=$('#form-recursos');const chosen=new Set();
 const count=$('#form-recursos-contagem');
 const sync=()=>{if(count)count.textContent=chosen.size?`${chosen.size} recurso(s) selecionado(s)`:'Nenhum recurso selecionado';};
 let resources=[];
 try{
   const data=await api('/api/recursos');resources=data.recursos||[];
   box.innerHTML=resources.map(r=>`<button type="button" class="match-chip" data-id="${Number(r.id_recurso)}" aria-pressed="false">${esc(r.nome_recurso)}</button>`).join('');
 }catch(e){box.innerHTML='<span class="muted small">Não foi possível carregar os recursos.</span>';invalidMessage(e)}
 const syncButtons=()=>{$$('button[data-id]',box).forEach(b=>{const yes=chosen.has(Number(b.dataset.id));b.classList.toggle('selected',yes);b.setAttribute('aria-pressed',String(yes))});sync()};
 box.addEventListener('click',e=>{const b=e.target.closest('button[data-id]');if(!b)return;const id=Number(b.dataset.id);if(chosen.has(id))chosen.delete(id);else chosen.add(id);syncButtons()});
 $('#limpar-form-recursos')?.addEventListener('click',()=>{chosen.clear();syncButtons()});
 if(mode==='editar'){
   try{const data=await api(`/api/anunciante/veiculo/${recordId}`);const v=data.veiculo;
      for(const [key,value] of Object.entries(v)){const control=form.elements.namedItem(key);if(control&&key!=='recursos'&&value!==null)control.value=value}
      for(const id of v.recursos||[])chosen.add(Number(id));syncButtons();
   }catch(e){invalidMessage(e)}
 }
 form.addEventListener('submit',async e=>{
    e.preventDefault();const obj=formObj(form);for(const k of ['ano','preco','quilometragem'])obj[k]=Number(obj[k]);obj.recursos=[...chosen];
    const btn=$('button[type="submit"]',form);btn.disabled=true;
    try{if(mode==='editar'){await api(`/api/veiculos/${recordId}`,{method:'PATCH',body:obj});aviso('Alterações salvas!')}else{await api('/api/veiculos',{method:'POST',body:obj});aviso('Anúncio publicado!')}setTimeout(()=>go('/anunciante'),900)}catch(err){invalidMessage(err)}finally{btn.disabled=false}
  });
}
document.addEventListener('DOMContentLoaded',async()=>{$$('img[data-categoria-foto]').forEach(img=>{const filename=img.dataset.categoriaFoto;img.src=FOTO_BASE+filename;img.dataset.backup=FOTO_ORIGEM[filename]||'';});const menu=$('#menu-btn'),links=$('#links');menu?.addEventListener('click',()=>{links.classList.toggle('open');menu.setAttribute('aria-expanded',String(links.classList.contains('open')))});const nav=$(`[data-nav="${page}"]`);if(nav)nav.classList.add('active');await sessionHeader();bindVehicleArea();({inicio:homeInit,login:loginInit,cadastro:cadastroInit,recuperar:recoveryInit,catalogo:catalogInit,match:matchInit,favoritos:favoritesInit,anunciante:advertiserInit} [page]||(()=>{}))();if($('#form-veiculo'))vehicleFormInit()});

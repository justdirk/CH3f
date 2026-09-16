'use strict';
const language=document.getElementById('language');
if(language)language.addEventListener('change',()=>{const target=new URL(language.value,location.origin);if(location.search)target.search=location.search;location.href=target.href;});
const form=document.getElementById('quote-form');
if(form){
 const config=JSON.parse(document.getElementById('quote-config').textContent);
 const result=document.getElementById('quote-result');
 let enquiry='';
 const selected=new URLSearchParams(location.search).get('product');
 if(selected&&Array.from(form.elements.interest.options).some(o=>o.value===selected))form.elements.interest.value=selected;
 function prepare(){
  if(!form.reportValidity())return {status:'invalid'};
  const data=new FormData(form),list=document.getElementById('summary-list');list.replaceChildren();
  const lines=['CH3F — '+config.summary,'',config.notSent,''];
  for(const [key,value] of data){
   const text=key==='interest'?form.elements.interest.selectedOptions[0].textContent:String(value).trim();
   if(!text)continue;
   const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=config[key];dd.textContent=text;row.append(dt,dd);list.append(row);lines.push(config[key]+': '+text);
  }
  enquiry=lines.join('\n');form.hidden=true;result.hidden=false;result.focus();return {status:'prepared_locally',sent:false};
 }
 form.addEventListener('submit',e=>{e.preventDefault();prepare();});
 document.getElementById('edit').addEventListener('click',()=>{result.hidden=true;form.hidden=false;form.elements.interest.focus();});
 document.getElementById('download').addEventListener('click',()=>{const u=URL.createObjectURL(new Blob([enquiry],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='CH3F-enquiry.txt';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1000);});
 if(document.modelContext?.registerTool){
  const lifecycle=new AbortController();
  try{Promise.resolve(document.modelContext.registerTool({name:'stage_ch3f_enquiry',title:'Prepare CH3F enquiry details',description:'Fill the visible CH3F enquiry form. Does not submit or send data. Use the visible button to prepare a local downloadable summary.',inputSchema:{type:'object',properties:{interest:{type:'string',enum:['electric','gas','knife80','knife120','both','advice']}},required:['interest'],additionalProperties:false},annotations:{readOnlyHint:false},execute(input){if(!input||typeof input!=='object'||Object.keys(input).some(k=>k!=='interest')||!['electric','gas','knife80','knife120','both','advice'].includes(input.interest))throw new Error('Invalid equipment selection');result.hidden=true;form.hidden=false;form.elements.interest.value=input.interest;form.elements.interest.focus();return {status:'staged',interest:form.elements.interest.value,sent:false};}},{signal:lifecycle.signal})).catch(()=>{});window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});}catch(e){}
 }
}
// Native details keeps the unconfigured WhatsApp preview usable without scripts.
const whatsappWidget=document.querySelector('.whatsapp-widget');
if(whatsappWidget){
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&whatsappWidget.open){whatsappWidget.open=false;whatsappWidget.querySelector('summary').focus();}});
 document.addEventListener('click',e=>{if(whatsappWidget.open&&!whatsappWidget.contains(e.target))whatsappWidget.open=false;});
}

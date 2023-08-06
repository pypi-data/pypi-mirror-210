"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[8464],{8464:(t,e,l)=>{l.r(e),l.d(e,{default:()=>d});var a=l(5872),n=l.n(a),s=l(55786),u=l(10581),i=l(61988),o=l(67294),r=l(4715),h=l(74448),c=l(11965);function d(t){var e;const{data:l,formData:a,height:d,width:g,setDataMask:v,setFocusedFilter:m,unsetFocusedFilter:p,setFilterActive:f,filterState:b,inputRef:w}=t,{defaultValue:S,multiSelect:Z}=a,[F,k]=(0,o.useState)(null!=S?S:[]),C=t=>{const e=(0,s.Z)(t);k(e);const l={};e.length&&(l.interactive_groupby=e),v({filterState:{value:e.length?e:null},extraFormData:l})};(0,o.useEffect)((()=>{C(b.value)}),[JSON.stringify(b.value),Z]),(0,o.useEffect)((()=>{C(null!=S?S:null)}),[JSON.stringify(S),Z]);const x=(0,s.Z)(a.groupby).map(u.Z),y=null!=(e=x[0])&&e.length?x[0]:null,D=y?l.filter((t=>y.includes(t.column_name))):l,_=l?D:[],A=0===_.length?(0,i.t)("No columns"):(0,i.tn)("%s option","%s options",_.length,_.length),K={};b.validateMessage&&(K.extra=(0,c.tZ)(h.Am,{status:b.validateStatus},b.validateMessage));const M=_.map((t=>{const{column_name:e,verbose_name:l}=t;return{label:null!=l?l:e,value:e}}));return(0,c.tZ)(h.un,{height:d,width:g},(0,c.tZ)(h.jp,n()({validateStatus:b.validateStatus},K),(0,c.tZ)(r.Ph,{allowClear:!0,value:F,placeholder:A,mode:Z?"multiple":void 0,onChange:C,onBlur:p,onFocus:m,ref:w,options:M,onDropdownVisibleChange:f})))}},74448:(t,e,l)=>{l.d(e,{un:()=>s,jp:()=>u,Am:()=>i});var a=l(51995),n=l(4591);const s=a.iK.div`
  min-height: ${({height:t})=>t}px;
  width: ${({width:t})=>t}px;
`,u=(0,a.iK)(n.Z)`
  &.ant-row.ant-form-item {
    margin: 0;
  }
`,i=a.iK.div`
  color: ${({theme:t,status:e="error"})=>{var l;return null==(l=t.colors[e])?void 0:l.base}};
`}}]);
//# sourceMappingURL=4876befc0369da74a0f3.chunk.js.map
(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[665],{45578:(e,t,a)=>{var r=a(67206),l=a(45652);e.exports=function(e,t){return e&&e.length?l(e,r(t,2)):[]}},26996:(e,t,a)=>{"use strict";a.d(t,{Z:()=>y});var r=a(67294),l=a(51995),i=a(61988),n=a(35932),o=a(74069),s=a(4715),d=a(34858),c=a(29487),u=a(11965);const p=(0,d.z)(),m=p?p.support:"https://superset.apache.org/docs/databases/installing-database-drivers",h=({errorMessage:e,showDbInstallInstructions:t})=>(0,u.tZ)(c.Z,{closable:!1,css:e=>(e=>u.iv`
  border: 1px solid ${e.colors.warning.light1};
  padding: ${4*e.gridUnit}px;
  margin: ${4*e.gridUnit}px 0;
  color: ${e.colors.warning.dark2};

  .ant-alert-message {
    margin: 0;
  }

  .ant-alert-description {
    font-size: ${e.typography.sizes.s+1}px;
    line-height: ${4*e.gridUnit}px;

    .ant-alert-icon {
      margin-right: ${2.5*e.gridUnit}px;
      font-size: ${e.typography.sizes.l+1}px;
      position: relative;
      top: ${e.gridUnit/4}px;
    }
  }
`)(e),type:"error",showIcon:!0,message:e,description:t?(0,u.tZ)(r.Fragment,null,(0,u.tZ)("br",null),(0,i.t)("Database driver for importing maybe not installed. Visit the Superset documentation page for installation instructions:"),(0,u.tZ)("a",{href:m,target:"_blank",rel:"noopener noreferrer",className:"additional-fields-alert-description"},(0,i.t)("here")),"."):""}),g=l.iK.div`
  display: block;
  color: ${({theme:e})=>e.colors.grayscale.base};
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
`,b=l.iK.div`
  padding-bottom: ${({theme:e})=>2*e.gridUnit}px;
  padding-top: ${({theme:e})=>2*e.gridUnit}px;

  & > div {
    margin: ${({theme:e})=>e.gridUnit}px 0;
  }

  &.extra-container {
    padding-top: 8px;
  }

  .confirm-overwrite {
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }

  .input-container {
    display: flex;
    align-items: center;

    label {
      display: flex;
      margin-right: ${({theme:e})=>2*e.gridUnit}px;
    }

    i {
      margin: 0 ${({theme:e})=>e.gridUnit}px;
    }
  }

  input,
  textarea {
    flex: 1 1 auto;
  }

  textarea {
    height: 160px;
    resize: none;
  }

  input::placeholder,
  textarea::placeholder {
    color: ${({theme:e})=>e.colors.grayscale.light1};
  }

  textarea,
  input[type='text'],
  input[type='number'] {
    padding: ${({theme:e})=>1.5*e.gridUnit}px
      ${({theme:e})=>2*e.gridUnit}px;
    border-style: none;
    border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    border-radius: ${({theme:e})=>e.gridUnit}px;

    &[name='name'] {
      flex: 0 1 auto;
      width: 40%;
    }

    &[name='sqlalchemy_uri'] {
      margin-right: ${({theme:e})=>3*e.gridUnit}px;
    }
  }
`,y=({resourceName:e,resourceLabel:t,passwordsNeededMessage:a,confirmOverwriteMessage:l,onModelImport:c,show:p,onHide:m,passwordFields:y=[],setPasswordFields:f=(()=>{})})=>{const[v,Z]=(0,r.useState)(!0),[w,_]=(0,r.useState)({}),[x,S]=(0,r.useState)(!1),[C,$]=(0,r.useState)(!1),[E,T]=(0,r.useState)([]),[k,I]=(0,r.useState)(!1),[N,A]=(0,r.useState)(),z=()=>{T([]),f([]),_({}),S(!1),$(!1),I(!1),A("")},{state:{alreadyExists:F,passwordsNeeded:H},importResource:D}=(0,d.PW)(e,t,(e=>{A(e)}));(0,r.useEffect)((()=>{f(H),H.length>0&&I(!1)}),[H,f]),(0,r.useEffect)((()=>{S(F.length>0),F.length>0&&I(!1)}),[F,S]);return v&&p&&Z(!1),(0,u.tZ)(o.Z,{name:"model",className:"import-model-modal",disablePrimaryButton:0===E.length||x&&!C||k,onHandledPrimaryAction:()=>{var e;(null==(e=E[0])?void 0:e.originFileObj)instanceof File&&(I(!0),D(E[0].originFileObj,w,C).then((e=>{e&&(z(),c())})))},onHide:()=>{Z(!0),m(),z()},primaryButtonName:x?(0,i.t)("Overwrite"):(0,i.t)("Import"),primaryButtonType:x?"danger":"primary",width:"750px",show:p,title:(0,u.tZ)("h4",null,(0,i.t)("Import %s",t))},(0,u.tZ)(b,null,(0,u.tZ)(s.gq,{name:"modelFile",id:"modelFile",accept:".yaml,.json,.yml,.zip",fileList:E,onChange:e=>{T([{...e.file,status:"done"}])},onRemove:e=>(T(E.filter((t=>t.uid!==e.uid))),!1),customRequest:()=>{},disabled:k},(0,u.tZ)(n.Z,{loading:k},"Select file"))),N&&(0,u.tZ)(h,{errorMessage:N,showDbInstallInstructions:y.length>0}),0===y.length?null:(0,u.tZ)(r.Fragment,null,(0,u.tZ)("h5",null,"Database passwords"),(0,u.tZ)(g,null,a),y.map((e=>(0,u.tZ)(b,{key:`password-for-${e}`},(0,u.tZ)("div",{className:"control-label"},e,(0,u.tZ)("span",{className:"required"},"*")),(0,u.tZ)("input",{name:`password-${e}`,autoComplete:`password-${e}`,type:"password",value:w[e],onChange:t=>_({...w,[e]:t.target.value})}))))),x?(0,u.tZ)(r.Fragment,null,(0,u.tZ)(b,null,(0,u.tZ)("div",{className:"confirm-overwrite"},l),(0,u.tZ)("div",{className:"control-label"},(0,i.t)('Type "%s" to confirm',(0,i.t)("OVERWRITE"))),(0,u.tZ)("input",{id:"overwrite",type:"text",onChange:e=>{var t,a;const r=null!=(t=null==(a=e.currentTarget)?void 0:a.value)?t:"";$(r.toUpperCase()===(0,i.t)("OVERWRITE"))}}))):null)}},13434:(e,t,a)=>{"use strict";a.r(t),a.d(t,{default:()=>P});var r=a(45578),l=a.n(r),i=a(51995),n=a(61988),o=a(11064),s=a(31069),d=a(67294),c=a(15926),u=a.n(c),p=a(30381),m=a.n(p),h=a(91877),g=a(93185),b=a(40768),y=a(34858),f=a(32228),v=a(19259),Z=a(20755),w=a(36674),_=a(18782),x=a(38703),S=a(61337),C=a(14114),$=a(83673),E=a(26996),T=a(58593),k=a(70163),I=a(1510),N=a(9312),A=a(8272),z=a(79789),F=a(85156),H=a(34024),D=a(11965);const M=i.iK.div`
  align-items: center;
  display: flex;

  a {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
  }

  svg {
    margin-right: ${({theme:e})=>e.gridUnit}px;
  }
`,U=(0,n.t)('The passwords for the databases below are needed in order to import them together with the charts. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in export files, and should be added manually after the import if they are needed.'),B=(0,n.t)("You are importing one or more charts that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?");(0,N.Z)();const O=(0,o.Z)(),L=async(e="",t,a)=>{var r;const i=e?{filters:[{col:"table_name",opr:"sw",value:e}]}:{},n=u().encode({columns:["datasource_name","datasource_id"],keys:["none"],order_column:"table_name",order_direction:"asc",page:t,page_size:a,...i}),{json:o={}}=await s.Z.get({endpoint:`/api/v1/dataset/?q=${n}`}),d=null==o||null==(r=o.result)?void 0:r.map((({table_name:e,id:t})=>({label:e,value:t})));return{data:l()(d,"value"),totalCount:null==o?void 0:o.count}},R=i.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.base};
`,P=(0,C.ZP)((function(e){var t,a;const{addDangerToast:r,addSuccessToast:l,user:{userId:i}}=e,{state:{loading:o,resourceCount:c,resourceCollection:p,bulkSelectEnabled:C},setResourceCollection:N,hasPerm:P,fetchData:V,toggleBulkSelect:q,refreshData:j}=(0,y.Yi)("chart",(0,n.t)("chart"),r),W=(0,d.useMemo)((()=>p.map((e=>e.id))),[p]),[Y,K]=(0,y.NE)("chart",W,r),{sliceCurrentlyEditing:X,handleChartUpdated:G,openChartEditModal:J,closeChartEditModal:Q}=(0,y.fF)(N,p),[ee,te]=(0,d.useState)(!1),[ae,re]=(0,d.useState)([]),[le,ie]=(0,d.useState)(!1),ne=(0,S.OH)(null==i?void 0:i.toString(),null),oe=P("can_write"),se=P("can_write"),de=P("can_write"),ce=P("can_export")&&(0,h.cr)(g.T.VERSIONED_EXPORT),ue=[{id:"changed_on_delta_humanized",desc:!0}],pe=null==F.b||null==(t=F.b.common)||null==(a=t.conf)?void 0:a.ENABLE_BROAD_ACTIVITY_ACCESS,me=e=>{const t=e.map((({id:e})=>e));(0,f.Z)("chart",t,(()=>{ie(!1)})),ie(!0)},he=e=>null!=e&&e.first_name?`${null==e?void 0:e.first_name} ${null==e?void 0:e.last_name}`:null,ge=(0,d.useMemo)((()=>[{Cell:({row:{original:{id:e}}})=>i&&(0,D.tZ)(w.Z,{itemId:e,saveFaveStar:Y,isStarred:K[e]}),Header:"",id:"id",disableSortBy:!0,size:"xs",hidden:!i},{Cell:({row:{original:{url:e,slice_name:t,certified_by:a,certification_details:r,description:l}}})=>(0,D.tZ)(M,null,(0,D.tZ)("a",{href:e},a&&(0,D.tZ)(d.Fragment,null,(0,D.tZ)(z.Z,{certifiedBy:a,details:r})," "),t),l&&(0,D.tZ)(A.Z,{tooltip:l,viewBox:"0 -1 24 24"})),Header:(0,n.t)("Chart"),accessor:"slice_name"},{Cell:({row:{original:{viz_type:e}}})=>{var t;return(null==(t=O.get(e))?void 0:t.name)||e},Header:(0,n.t)("Visualization type"),accessor:"viz_type",size:"xxl"},{Cell:({row:{original:{datasource_name_text:e,datasource_url:t}}})=>(0,D.tZ)("a",{href:t},e),Header:(0,n.t)("Dataset"),accessor:"datasource_id",disableSortBy:!0,size:"xl"},{Cell:({row:{original:{last_saved_by:e,changed_by_url:t}}})=>pe?(0,D.tZ)("a",{href:t},he(e)):(0,D.tZ)(d.Fragment,null,he(e)),Header:(0,n.t)("Modified by"),accessor:"last_saved_by.first_name",size:"xl"},{Cell:({row:{original:{last_saved_at:e}}})=>(0,D.tZ)("span",{className:"no-wrap"},e?m().utc(e).fromNow():null),Header:(0,n.t)("Last modified"),accessor:"last_saved_at",size:"xl"},{accessor:"owners",hidden:!0,disableSortBy:!0},{Cell:({row:{original:{created_by:e}}})=>e?`${e.first_name} ${e.last_name}`:"",Header:(0,n.t)("Created by"),accessor:"created_by",disableSortBy:!0,size:"xl"},{Cell:({row:{original:e}})=>se||de||ce?(0,D.tZ)(R,{className:"actions"},de&&(0,D.tZ)(v.Z,{title:(0,n.t)("Please confirm"),description:(0,D.tZ)(d.Fragment,null,(0,n.t)("Are you sure you want to delete")," ",(0,D.tZ)("b",null,e.slice_name),"?"),onConfirm:()=>(0,b.Gm)(e,l,r,j)},(e=>(0,D.tZ)(T.u,{id:"delete-action-tooltip",title:(0,n.t)("Delete"),placement:"bottom"},(0,D.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:e},(0,D.tZ)(k.Z.Trash,null))))),ce&&(0,D.tZ)(T.u,{id:"export-action-tooltip",title:(0,n.t)("Export"),placement:"bottom"},(0,D.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>me([e])},(0,D.tZ)(k.Z.Share,null))),se&&(0,D.tZ)(T.u,{id:"edit-action-tooltip",title:(0,n.t)("Edit"),placement:"bottom"},(0,D.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>J(e)},(0,D.tZ)(k.Z.EditAlt,null)))):null,Header:(0,n.t)("Actions"),id:"actions",disableSortBy:!0,hidden:!se&&!de}]),[i,se,de,ce,Y,K,j,l,r]),be=(0,d.useMemo)((()=>({Header:(0,n.t)("Favorite"),id:"id",urlDisplay:"favorite",input:"select",operator:_.p.chartIsFav,unfilteredLabel:(0,n.t)("Any"),selects:[{label:(0,n.t)("Yes"),value:!0},{label:(0,n.t)("No"),value:!1}]})),[]),ye=(0,d.useMemo)((()=>[{Header:(0,n.t)("Owner"),id:"owners",input:"select",operator:_.p.relationManyMany,unfilteredLabel:(0,n.t)("All"),fetchSelects:(0,b.tm)("chart","owners",(0,b.v$)((e=>r((0,n.t)("An error occurred while fetching chart owners values: %s",e)))),e.user),paginate:!0},{Header:(0,n.t)("Created by"),id:"created_by",input:"select",operator:_.p.relationOneMany,unfilteredLabel:(0,n.t)("All"),fetchSelects:(0,b.tm)("chart","created_by",(0,b.v$)((e=>r((0,n.t)("An error occurred while fetching chart created by values: %s",e)))),e.user),paginate:!0},{Header:(0,n.t)("Chart type"),id:"viz_type",input:"select",operator:_.p.equals,unfilteredLabel:(0,n.t)("All"),selects:O.keys().filter((e=>{var t;return(0,I.X3)((null==(t=O.get(e))?void 0:t.behaviors)||[])})).map((e=>{var t;return{label:(null==(t=O.get(e))?void 0:t.name)||e,value:e}})).sort(((e,t)=>e.label&&t.label?e.label>t.label?1:e.label<t.label?-1:0:0))},{Header:(0,n.t)("Dataset"),id:"datasource_id",input:"select",operator:_.p.equals,unfilteredLabel:(0,n.t)("All"),fetchSelects:L,paginate:!0},...i?[be]:[],{Header:(0,n.t)("Certified"),id:"id",urlDisplay:"certified",input:"select",operator:_.p.chartIsCertified,unfilteredLabel:(0,n.t)("Any"),selects:[{label:(0,n.t)("Yes"),value:!0},{label:(0,n.t)("No"),value:!1}]},{Header:(0,n.t)("Search"),id:"slice_name",input:"search",operator:_.p.chartAllText}]),[r,be,e.user]),fe=[{desc:!1,id:"slice_name",label:(0,n.t)("Alphabetical"),value:"alphabetical"},{desc:!0,id:"changed_on_delta_humanized",label:(0,n.t)("Recently modified"),value:"recently_modified"},{desc:!1,id:"changed_on_delta_humanized",label:(0,n.t)("Least recently modified"),value:"least_recently_modified"}],ve=(0,d.useCallback)((e=>(0,D.tZ)(H.Z,{chart:e,showThumbnails:ne?ne.thumbnails:(0,h.cr)(g.T.THUMBNAILS),hasPerm:P,openChartEditModal:J,bulkSelectEnabled:C,addDangerToast:r,addSuccessToast:l,refreshData:j,userId:i,loading:o,favoriteStatus:K[e.id],saveFavoriteStatus:Y,handleBulkChartExport:me})),[r,l,C,K,P,o]),Ze=[];return(de||ce)&&Ze.push({name:(0,n.t)("Bulk select"),buttonStyle:"secondary","data-test":"bulk-select",onClick:q}),oe&&(Ze.push({name:(0,D.tZ)(d.Fragment,null,(0,D.tZ)("i",{className:"fa fa-plus"})," ",(0,n.t)("Chart")),buttonStyle:"primary",onClick:()=>{window.location.assign("/chart/add")}}),(0,h.cr)(g.T.VERSIONED_EXPORT)&&Ze.push({name:(0,D.tZ)(T.u,{id:"import-tooltip",title:(0,n.t)("Import charts"),placement:"bottomRight"},(0,D.tZ)(k.Z.Import,null)),buttonStyle:"link",onClick:()=>{te(!0)}})),(0,D.tZ)(d.Fragment,null,(0,D.tZ)(Z.Z,{name:(0,n.t)("Charts"),buttons:Ze}),X&&(0,D.tZ)($.Z,{onHide:Q,onSave:G,show:!0,slice:X}),(0,D.tZ)(v.Z,{title:(0,n.t)("Please confirm"),description:(0,n.t)("Are you sure you want to delete the selected charts?"),onConfirm:function(e){s.Z.delete({endpoint:`/api/v1/chart/?q=${u().encode(e.map((({id:e})=>e)))}`}).then((({json:e={}})=>{j(),l(e.message)}),(0,b.v$)((e=>r((0,n.t)("There was an issue deleting the selected charts: %s",e)))))}},(e=>{const t=[];return de&&t.push({key:"delete",name:(0,n.t)("Delete"),type:"danger",onSelect:e}),ce&&t.push({key:"export",name:(0,n.t)("Export"),type:"primary",onSelect:me}),(0,D.tZ)(_.Z,{bulkActions:t,bulkSelectEnabled:C,cardSortSelectOptions:fe,className:"chart-list-view",columns:ge,count:c,data:p,disableBulkSelect:q,fetchData:V,filters:ye,initialSort:ue,loading:o,pageSize:25,renderCard:ve,showThumbnails:ne?ne.thumbnails:(0,h.cr)(g.T.THUMBNAILS),defaultViewMode:(0,h.cr)(g.T.LISTVIEWS_DEFAULT_CARD_VIEW)?"card":"table"})})),(0,D.tZ)(E.Z,{resourceName:"chart",resourceLabel:(0,n.t)("chart"),passwordsNeededMessage:U,confirmOverwriteMessage:B,addDangerToast:r,addSuccessToast:l,onModelImport:()=>{te(!1),j(),l((0,n.t)("Chart imported"))},show:ee,onHide:()=>{te(!1)},passwordFields:ae,setPasswordFields:re}),le&&(0,D.tZ)(x.Z,null))}))}}]);
//# sourceMappingURL=91467320f2a38b710651.chunk.js.map
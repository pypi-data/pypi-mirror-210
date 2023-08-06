"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[8774],{26996:(e,t,a)=>{a.d(t,{Z:()=>y});var r=a(67294),i=a(51995),o=a(61988),l=a(35932),s=a(74069),n=a(4715),d=a(34858),u=a(29487),c=a(11965);const h=(0,d.z)(),p=h?h.support:"https://superset.apache.org/docs/databases/installing-database-drivers",m=({errorMessage:e,showDbInstallInstructions:t})=>(0,c.tZ)(u.Z,{closable:!1,css:e=>(e=>c.iv`
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
`)(e),type:"error",showIcon:!0,message:e,description:t?(0,c.tZ)(r.Fragment,null,(0,c.tZ)("br",null),(0,o.t)("Database driver for importing maybe not installed. Visit the Superset documentation page for installation instructions:"),(0,c.tZ)("a",{href:p,target:"_blank",rel:"noopener noreferrer",className:"additional-fields-alert-description"},(0,o.t)("here")),"."):""}),b=i.iK.div`
  display: block;
  color: ${({theme:e})=>e.colors.grayscale.base};
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
`,g=i.iK.div`
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
`,y=({resourceName:e,resourceLabel:t,passwordsNeededMessage:a,confirmOverwriteMessage:i,onModelImport:u,show:h,onHide:p,passwordFields:y=[],setPasswordFields:f=(()=>{})})=>{const[Z,_]=(0,r.useState)(!0),[w,v]=(0,r.useState)({}),[S,x]=(0,r.useState)(!1),[C,$]=(0,r.useState)(!1),[I,T]=(0,r.useState)([]),[E,D]=(0,r.useState)(!1),[k,N]=(0,r.useState)(),A=()=>{T([]),f([]),v({}),x(!1),$(!1),D(!1),N("")},{state:{alreadyExists:F,passwordsNeeded:H},importResource:z}=(0,d.PW)(e,t,(e=>{N(e)}));(0,r.useEffect)((()=>{f(H),H.length>0&&D(!1)}),[H,f]),(0,r.useEffect)((()=>{x(F.length>0),F.length>0&&D(!1)}),[F,x]);return Z&&h&&_(!1),(0,c.tZ)(s.Z,{name:"model",className:"import-model-modal",disablePrimaryButton:0===I.length||S&&!C||E,onHandledPrimaryAction:()=>{var e;(null==(e=I[0])?void 0:e.originFileObj)instanceof File&&(D(!0),z(I[0].originFileObj,w,C).then((e=>{e&&(A(),u())})))},onHide:()=>{_(!0),p(),A()},primaryButtonName:S?(0,o.t)("Overwrite"):(0,o.t)("Import"),primaryButtonType:S?"danger":"primary",width:"750px",show:h,title:(0,c.tZ)("h4",null,(0,o.t)("Import %s",t))},(0,c.tZ)(g,null,(0,c.tZ)(n.gq,{name:"modelFile",id:"modelFile",accept:".yaml,.json,.yml,.zip",fileList:I,onChange:e=>{T([{...e.file,status:"done"}])},onRemove:e=>(T(I.filter((t=>t.uid!==e.uid))),!1),customRequest:()=>{},disabled:E},(0,c.tZ)(l.Z,{loading:E},"Select file"))),k&&(0,c.tZ)(m,{errorMessage:k,showDbInstallInstructions:y.length>0}),0===y.length?null:(0,c.tZ)(r.Fragment,null,(0,c.tZ)("h5",null,"Database passwords"),(0,c.tZ)(b,null,a),y.map((e=>(0,c.tZ)(g,{key:`password-for-${e}`},(0,c.tZ)("div",{className:"control-label"},e,(0,c.tZ)("span",{className:"required"},"*")),(0,c.tZ)("input",{name:`password-${e}`,autoComplete:`password-${e}`,type:"password",value:w[e],onChange:t=>v({...w,[e]:t.target.value})}))))),S?(0,c.tZ)(r.Fragment,null,(0,c.tZ)(g,null,(0,c.tZ)("div",{className:"confirm-overwrite"},i),(0,c.tZ)("div",{className:"control-label"},(0,o.t)('Type "%s" to confirm',(0,o.t)("OVERWRITE"))),(0,c.tZ)("input",{id:"overwrite",type:"text",onChange:e=>{var t,a;const r=null!=(t=null==(a=e.currentTarget)?void 0:a.value)?t:"";$(r.toUpperCase()===(0,o.t)("OVERWRITE"))}}))):null)}},23767:(e,t,a)=>{a.r(t),a.d(t,{default:()=>H});var r,i=a(61988),o=a(51995),l=a(31069),s=a(67294),n=a(73727),d=a(15926),u=a.n(d),c=a(91877),h=a(93185),p=a(40768),m=a(34858),b=a(19259),g=a(32228),y=a(38703),f=a(20755),Z=a(18782),_=a(61337),w=a(14114),v=a(34581),S=a(70163),x=a(36674),C=a(20818),$=a(58593),I=a(26996),T=a(79789),E=a(85156),D=a(99415);!function(e){e.PUBLISHED="published",e.DRAFT="draft"}(r||(r={}));var k=a(11965);const N=(0,i.t)('The passwords for the databases below are needed in order to import them together with the dashboards. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in export files, and should be added manually after the import if they are needed.'),A=(0,i.t)("You are importing one or more dashboards that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?"),F=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.base};
`,H=(0,w.ZP)((function(e){var t,a;const{addDangerToast:o,addSuccessToast:d,user:{userId:w}}=e,{state:{loading:H,resourceCount:z,resourceCollection:U,bulkSelectEnabled:M},setResourceCollection:O,hasPerm:B,fetchData:P,toggleBulkSelect:R,refreshData:L}=(0,m.Yi)("dashboard",(0,i.t)("dashboard"),o),V=(0,s.useMemo)((()=>U.map((e=>e.id))),[U]),[j,q]=(0,m.NE)("dashboard",V,o),[W,Y]=(0,s.useState)(null),[K,X]=(0,s.useState)(!1),[G,J]=(0,s.useState)([]),[Q,ee]=(0,s.useState)(!1),te=null==E.b||null==(t=E.b.common)||null==(a=t.conf)?void 0:a.ENABLE_BROAD_ACTIVITY_ACCESS,ae=(0,_.OH)(null==w?void 0:w.toString(),null),re=B("can_write"),ie=B("can_write"),oe=B("can_write"),le=B("can_export")&&(0,c.cr)(h.T.VERSIONED_EXPORT),se=[{id:"changed_on_delta_humanized",desc:!0}];function ne(e){Y(e)}function de(e){return l.Z.get({endpoint:`/api/v1/dashboard/${e.id}`}).then((({json:e={}})=>{O(U.map((t=>{var a;if(t.id===(null==e||null==(a=e.result)?void 0:a.id)){const{changed_by_name:a,changed_by_url:r,changed_by:i,dashboard_title:o="",slug:l="",json_metadata:s="",changed_on_delta_humanized:n,url:d="",certified_by:u="",certification_details:c=""}=e.result;return{...t,changed_by_name:a,changed_by_url:r,changed_by:i,dashboard_title:o,slug:l,json_metadata:s,changed_on_delta_humanized:n,url:d,certified_by:u,certification_details:c}}return t})))}),(0,p.v$)((e=>o((0,i.t)("An error occurred while fetching dashboards: %s",e)))))}const ue=e=>{const t=e.map((({id:e})=>e));(0,g.Z)("dashboard",t,(()=>{ee(!1)})),ee(!0)},ce=(0,s.useMemo)((()=>[{Cell:({row:{original:{id:e}}})=>w&&(0,k.tZ)(x.Z,{itemId:e,saveFaveStar:j,isStarred:q[e]}),Header:"",id:"id",disableSortBy:!0,size:"xs",hidden:!w},{Cell:({row:{original:{url:e,dashboard_title:t,certified_by:a,certification_details:r}}})=>(0,k.tZ)(n.rU,{to:e},a&&(0,k.tZ)(s.Fragment,null,(0,k.tZ)(T.Z,{certifiedBy:a,details:r})," "),t),Header:(0,i.t)("Title"),accessor:"dashboard_title"},{Cell:({row:{original:{changed_by_name:e,changed_by_url:t}}})=>te?(0,k.tZ)("a",{href:t},e):(0,k.tZ)(s.Fragment,null,e),Header:(0,i.t)("Modified by"),accessor:"changed_by.first_name",size:"xl"},{Cell:({row:{original:{status:e}}})=>e===r.PUBLISHED?(0,i.t)("Published"):(0,i.t)("Draft"),Header:(0,i.t)("Status"),accessor:"published",size:"xl"},{Cell:({row:{original:{changed_on_delta_humanized:e}}})=>(0,k.tZ)("span",{className:"no-wrap"},e),Header:(0,i.t)("Modified"),accessor:"changed_on_delta_humanized",size:"xl"},{Cell:({row:{original:{created_by:e}}})=>e?`${e.first_name} ${e.last_name}`:"",Header:(0,i.t)("Created by"),accessor:"created_by",disableSortBy:!0,size:"xl"},{Cell:({row:{original:{owners:e=[]}}})=>(0,k.tZ)(v.Z,{users:e}),Header:(0,i.t)("Owners"),accessor:"owners",disableSortBy:!0,size:"xl"},{Cell:({row:{original:e}})=>(0,k.tZ)(F,{className:"actions"},oe&&(0,k.tZ)(b.Z,{title:(0,i.t)("Please confirm"),description:(0,k.tZ)(s.Fragment,null,(0,i.t)("Are you sure you want to delete")," ",(0,k.tZ)("b",null,e.dashboard_title),"?"),onConfirm:()=>(0,p.Iu)(e,L,d,o)},(e=>(0,k.tZ)($.u,{id:"delete-action-tooltip",title:(0,i.t)("Delete"),placement:"bottom"},(0,k.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:e},(0,k.tZ)(S.Z.Trash,null))))),le&&(0,k.tZ)($.u,{id:"export-action-tooltip",title:(0,i.t)("Export"),placement:"bottom"},(0,k.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>ue([e])},(0,k.tZ)(S.Z.Share,null))),ie&&(0,k.tZ)($.u,{id:"edit-action-tooltip",title:(0,i.t)("Edit"),placement:"bottom"},(0,k.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>ne(e)},(0,k.tZ)(S.Z.EditAlt,null)))),Header:(0,i.t)("Actions"),id:"actions",hidden:!ie&&!oe&&!le,disableSortBy:!0}]),[w,ie,oe,le,j,q,L,d,o]),he=(0,s.useMemo)((()=>({Header:(0,i.t)("Favorite"),id:"id",urlDisplay:"favorite",input:"select",operator:Z.p.dashboardIsFav,unfilteredLabel:(0,i.t)("Any"),selects:[{label:(0,i.t)("Yes"),value:!0},{label:(0,i.t)("No"),value:!1}]})),[]),pe=(0,s.useMemo)((()=>[{Header:(0,i.t)("Owner"),id:"owners",input:"select",operator:Z.p.relationManyMany,unfilteredLabel:(0,i.t)("All"),fetchSelects:(0,p.tm)("dashboard","owners",(0,p.v$)((e=>o((0,i.t)("An error occurred while fetching dashboard owner values: %s",e)))),e.user),paginate:!0},{Header:(0,i.t)("Created by"),id:"created_by",input:"select",operator:Z.p.relationOneMany,unfilteredLabel:(0,i.t)("All"),fetchSelects:(0,p.tm)("dashboard","created_by",(0,p.v$)((e=>o((0,i.t)("An error occurred while fetching dashboard created by values: %s",e)))),e.user),paginate:!0},{Header:(0,i.t)("Status"),id:"published",input:"select",operator:Z.p.equals,unfilteredLabel:(0,i.t)("Any"),selects:[{label:(0,i.t)("Published"),value:!0},{label:(0,i.t)("Draft"),value:!1}]},...w?[he]:[],{Header:(0,i.t)("Certified"),id:"id",urlDisplay:"certified",input:"select",operator:Z.p.dashboardIsCertified,unfilteredLabel:(0,i.t)("Any"),selects:[{label:(0,i.t)("Yes"),value:!0},{label:(0,i.t)("No"),value:!1}]},{Header:(0,i.t)("Search"),id:"dashboard_title",input:"search",operator:Z.p.titleOrSlug}]),[o,he,e.user]),me=[{desc:!1,id:"dashboard_title",label:(0,i.t)("Alphabetical"),value:"alphabetical"},{desc:!0,id:"changed_on_delta_humanized",label:(0,i.t)("Recently modified"),value:"recently_modified"},{desc:!1,id:"changed_on_delta_humanized",label:(0,i.t)("Least recently modified"),value:"least_recently_modified"}],be=(0,s.useCallback)((e=>(0,k.tZ)(D.Z,{dashboard:e,hasPerm:B,bulkSelectEnabled:M,refreshData:L,showThumbnails:ae?ae.thumbnails:(0,c.cr)(h.T.THUMBNAILS),userId:w,loading:H,addDangerToast:o,addSuccessToast:d,openDashboardEditModal:ne,saveFavoriteStatus:j,favoriteStatus:q[e.id],handleBulkDashboardExport:ue})),[o,d,M,q,B,H,w,L,j,ae]),ge=[];return(oe||le)&&ge.push({name:(0,i.t)("Bulk select"),buttonStyle:"secondary","data-test":"bulk-select",onClick:R}),re&&(ge.push({name:(0,k.tZ)(s.Fragment,null,(0,k.tZ)("i",{className:"fa fa-plus"})," ",(0,i.t)("Dashboard")),buttonStyle:"primary",onClick:()=>{window.location.assign("/dashboard/new")}}),(0,c.cr)(h.T.VERSIONED_EXPORT)&&ge.push({name:(0,k.tZ)($.u,{id:"import-tooltip",title:(0,i.t)("Import dashboards"),placement:"bottomRight"},(0,k.tZ)(S.Z.Import,null)),buttonStyle:"link",onClick:()=>{X(!0)}})),(0,k.tZ)(s.Fragment,null,(0,k.tZ)(f.Z,{name:(0,i.t)("Dashboards"),buttons:ge}),(0,k.tZ)(b.Z,{title:(0,i.t)("Please confirm"),description:(0,i.t)("Are you sure you want to delete the selected dashboards?"),onConfirm:function(e){return l.Z.delete({endpoint:`/api/v1/dashboard/?q=${u().encode(e.map((({id:e})=>e)))}`}).then((({json:e={}})=>{L(),d(e.message)}),(0,p.v$)((e=>o((0,i.t)("There was an issue deleting the selected dashboards: ",e)))))}},(e=>{const t=[];return oe&&t.push({key:"delete",name:(0,i.t)("Delete"),type:"danger",onSelect:e}),le&&t.push({key:"export",name:(0,i.t)("Export"),type:"primary",onSelect:ue}),(0,k.tZ)(s.Fragment,null,W&&(0,k.tZ)(C.Z,{dashboardId:W.id,show:!0,onHide:()=>Y(null),onSubmit:de}),(0,k.tZ)(Z.Z,{bulkActions:t,bulkSelectEnabled:M,cardSortSelectOptions:me,className:"dashboard-list-view",columns:ce,count:z,data:U,disableBulkSelect:R,fetchData:P,filters:pe,initialSort:se,loading:H,pageSize:25,showThumbnails:ae?ae.thumbnails:(0,c.cr)(h.T.THUMBNAILS),renderCard:be,defaultViewMode:(0,c.cr)(h.T.LISTVIEWS_DEFAULT_CARD_VIEW)?"card":"table"}))})),(0,k.tZ)(I.Z,{resourceName:"dashboard",resourceLabel:(0,i.t)("dashboard"),passwordsNeededMessage:N,confirmOverwriteMessage:A,addDangerToast:o,addSuccessToast:d,onModelImport:()=>{X(!1),L(),d((0,i.t)("Dashboard imported"))},show:K,onHide:()=>{X(!1)},passwordFields:G,setPasswordFields:J}),Q&&(0,k.tZ)(y.Z,null))}))}}]);
//# sourceMappingURL=5747becdbcfda2f19db0.chunk.js.map
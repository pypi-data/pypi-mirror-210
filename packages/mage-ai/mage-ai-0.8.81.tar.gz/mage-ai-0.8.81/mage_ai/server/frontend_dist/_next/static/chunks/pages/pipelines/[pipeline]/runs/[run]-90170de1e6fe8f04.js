(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[8662],{27125:function(e,n,t){"use strict";var r=t(82684),i=t(12691),u=t.n(i),o=t(34376),l=t.n(o),c=t(9518),s=t(66050),a=t(60328),d=t(16634),p=t(10919),f=t(98781),v=t(86673),b=t(58180),h=t(19711),j=t(10503),O=t(49125),g=t(44162),m=t(24224),x=t(28598);n.Z=function(e){var n=e.blockRuns,t=e.onClickRow,i=e.pipeline,o=e.selectedRun,y=(0,r.useContext)(c.ThemeContext),Z=(i||{}).uuid,P=(0,r.useMemo)((function(){return i.blocks||[]}),[i]),_=(0,r.useMemo)((function(){return(0,m.HK)(P,(function(e){return e.uuid}))}),[P]);return(0,x.jsx)(b.Z,{columnFlex:[null,1,3,2,null,null],columns:[{uuid:"Date"},{uuid:"Status"},{uuid:"Trigger"},{uuid:"Block"},{uuid:"Completed"},{uuid:"Logs"}],isSelectedRow:function(e){return n[e].id===(null===o||void 0===o?void 0:o.id)},onClickRow:t,rows:null===n||void 0===n?void 0:n.map((function(e){var n,t,r,o,c=e.block_uuid,b=e.completed_at,m=e.created_at,P=e.id,D=e.pipeline_schedule_id,k=e.pipeline_schedule_name,w=e.status,E=c,T=E.split(":");f.qL.INTEGRATION===i.type&&(E=T[0],r=T[1],o=T[2]);var N=_[E];return N||(N=_[T[0]]),[(0,x.jsx)(h.ZP,{monospace:!0,default:!0,children:m}),(0,x.jsx)(h.ZP,{danger:s.V.FAILED===w,default:s.V.CANCELLED===w,info:s.V.INITIAL===w,monospace:!0,success:s.V.COMPLETED===w,warning:s.V.RUNNING===w,children:w}),(0,x.jsx)(u(),{as:"/pipelines/".concat(Z,"/triggers/").concat(D),href:"/pipelines/[pipeline]/triggers/[...slug]",passHref:!0,children:(0,x.jsx)(p.Z,{bold:!0,sameColorAsText:!0,children:k})}),(0,x.jsx)(u(),{as:"/pipelines/".concat(Z,"/edit?block_uuid=").concat(E),href:"/pipelines/[pipeline]/edit",passHref:!0,children:(0,x.jsxs)(p.Z,{bold:!0,sameColorAsText:!0,verticalAlignContent:!0,children:[(0,x.jsx)(d.Z,{color:(0,g.qn)(null===(n=N)||void 0===n?void 0:n.type,{blockColor:null===(t=N)||void 0===t?void 0:t.color,theme:y}).accent,size:1.5*O.iI,square:!0}),(0,x.jsx)(v.Z,{mr:1}),(0,x.jsxs)(h.ZP,{monospace:!0,children:[E,r&&": ",r&&(0,x.jsx)(h.ZP,{default:!0,inline:!0,monospace:!0,children:r}),o>=0&&": ",o>=0&&(0,x.jsx)(h.ZP,{default:!0,inline:!0,monospace:!0,children:o})]})]})}),(0,x.jsx)(h.ZP,{monospace:!0,default:!0,children:b||"-"}),(0,x.jsx)(a.Z,{default:!0,iconOnly:!0,noBackground:!0,onClick:function(){return l().push("/pipelines/".concat(Z,"/logs?block_run_id[]=").concat(P))},children:(0,x.jsx)(j.B4,{default:!0,size:2*O.iI})})]})),uuid:"block-runs"})}},56681:function(e,n,t){"use strict";t.d(n,{G7:function(){return y},ZP:function(){return Z},u$:function(){return g}});var r=t(75582),i=t(82394),u=t(26304),o=t(32316),l=t(22673),c=t(48957),s=t(86673),a=t(19711),d=t(58180),p=t(49125),f=t(19395),v=t(7715),b=t(28598),h=["height","heightOffset","pipeline","selectedRun","selectedTab","setSelectedTab"];function j(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,r)}return t}function O(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?j(Object(t),!0).forEach((function(n){(0,i.Z)(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):j(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}var g=76,m={uuid:"Run details"},x={uuid:"Dependency tree"},y=[x,m];function Z(e){var n=e.height,t=e.heightOffset,i=e.pipeline,j=e.selectedRun,Z=e.selectedTab,P=e.setSelectedTab,_=O({},(0,u.Z)(e,h));j?_.blockStatus=(0,f.IJ)(null===j||void 0===j?void 0:j.block_runs):_.noStatus=!0;var D=(0,v.Kn)(null===j||void 0===j?void 0:j.variables)?O({},null===j||void 0===j?void 0:j.variables):(null===j||void 0===j?void 0:j.variables)||{},k=null===j||void 0===j?void 0:j.event_variables;if(k&&(0,v.Kn)(k)&&!(0,v.Qr)(k))if((0,v.Kn)(D)&&D.hasOwnProperty("event")){var w=(0,v.Kn)(D.event)?D.event:{};D.event=O(O({},w),k)}else D.event=O({},k);var E=[];D&&JSON.stringify(D,null,2).split("\n").forEach((function(e){E.push("    ".concat(e))}));var T=j&&[["Run ID",null===j||void 0===j?void 0:j.id],["Variables",(0,b.jsx)(l.Z,{language:"json",small:!0,source:E.join("\n")},"variable_value")]],N=j&&(0,b.jsx)(s.Z,{pb:p.cd,px:p.cd,children:(0,b.jsx)(d.Z,{alignTop:!0,columnFlex:[null,1],columnMaxWidth:function(e){return 1===e?"100px":null},rows:T.map((function(e,n){var t=(0,r.Z)(e,2),i=t[0],u=t[1];return[(0,b.jsx)(a.ZP,{monospace:!0,muted:!0,children:i},"key_".concat(n)),(0,b.jsx)(a.ZP,{monospace:!0,textOverflow:!0,children:u},"val_".concat(n))]})),uuid:"LogDetail"})}),C=Z&&P;return(0,b.jsxs)(b.Fragment,{children:[C&&(0,b.jsx)(s.Z,{py:p.cd,children:(0,b.jsx)(o.Z,{onClickTab:P,selectedTabUUID:null===Z||void 0===Z?void 0:Z.uuid,tabs:y})}),(!C||x.uuid===(null===Z||void 0===Z?void 0:Z.uuid))&&(0,b.jsx)(c.Z,O(O({},_),{},{height:n,heightOffset:(t||0)+(C?g:0),pipeline:i})),m.uuid===(null===Z||void 0===Z?void 0:Z.uuid)&&N]})}},19395:function(e,n,t){"use strict";t.d(n,{IJ:function(){return a},Vx:function(){return p},eI:function(){return d},gU:function(){return v},tL:function(){return f},vJ:function(){return b}});var r,i,u=t(82394),o=t(92083),l=t.n(o);function c(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,r)}return t}function s(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?c(Object(t),!0).forEach((function(n){(0,u.Z)(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):c(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function a(e){return null===e||void 0===e?void 0:e.reduce((function(e,n){var t=n.block_uuid,r=n.completed_at,i=n.started_at,o=n.status,c=null;i&&r&&(c=l()(r).valueOf()-l()(i).valueOf());return s(s({},e),{},(0,u.Z)({},t,{runtime:c,status:o}))}),{})}function d(e){if(!e)return null;var n=new Date(l()(e).valueOf()),t=Date.UTC(n.getFullYear(),n.getMonth(),n.getDate(),n.getHours(),n.getMinutes(),n.getSeconds());return new Date(t)}function p(e){return"string"!==typeof e?e:d(e.split("+")[0]).toISOString().split(".")[0]}!function(e){e.DAY="day",e.HOUR="hour",e.MINUTE="minute",e.SECOND="second"}(i||(i={}));var f=(r={},(0,u.Z)(r,i.DAY,86400),(0,u.Z)(r,i.HOUR,3600),(0,u.Z)(r,i.MINUTE,60),(0,u.Z)(r,i.SECOND,1),r);function v(e){var n=i.SECOND,t=e;return e%86400===0?(t/=86400,n=i.DAY):e%3600===0?(t/=3600,n=i.HOUR):e%60===0&&(t/=60,n=i.MINUTE),{time:t,unit:n}}function b(e,n){return e*f[n]}},47409:function(e,n,t){"use strict";t.d(n,{Az:function(){return l},BF:function(){return o},Do:function(){return s},VO:function(){return u},sZ:function(){return c}});var r,i=t(82394),u=t(66050).V,o=[u.INITIAL,u.RUNNING],l=[u.CANCELLED,u.COMPLETED,u.FAILED],c="__mage_variables",s=(r={},(0,i.Z)(r,u.CANCELLED,"Cancelled"),(0,i.Z)(r,u.COMPLETED,"Done"),(0,i.Z)(r,u.FAILED,"Failed"),(0,i.Z)(r,u.INITIAL,"Ready"),(0,i.Z)(r,u.RUNNING,"Running"),r)},23588:function(e,n,t){"use strict";t.r(n),t.d(n,{default:function(){return K}});var r=t(77837),i=t(75582),u=t(82394),o=t(38860),l=t.n(o),c=t(82684),s=t(83455),a=t(27125),d=t(60328),p=t(34744),f=t(93461),v=t(67971),b=t(87372),h=t(60547),j=t(47409),O=t(98781),g=t(41788),m=t(86673),x=t(54283),y=t(19711),Z=t(82531),P=t(26304),_=t(32316),D=t(62976),k=t(48957),w=t(82635),E=t(49125),T=t(64155),N=t(56681),C=t(19395),I=t(90211),R=t(28598),S=["blockRuns","columns","dataType","height","heightOffset","loadingData","pipeline","renderColumnHeader","rows","selectedRun","selectedTab","setSelectedTab","textData"];function L(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,r)}return t}function A(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?L(Object(t),!0).forEach((function(n){(0,u.Z)(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):L(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}var M={uuid:"Dependency tree"},U={uuid:"Block output"},F=[M,U];var B=t(59920),H=t(96510),V=t(66653);function G(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);n&&(r=r.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,r)}return t}function q(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?G(Object(t),!0).forEach((function(n){(0,u.Z)(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):G(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function J(e){var n,t=e.pipeline,r=e.pipelineRun,u=(0,c.useState)(null),o=u[0],l=u[1],g=(0,c.useState)(F[0]),L=g[0],G=g[1],J=(0,c.useState)(null),K=J[0],Y=J[1],z=t.uuid,W=Z.ZP.pipelines.detail(z,{includes_content:!1,includes_outputs:!1},{revalidateOnFocus:!1}).data,X=(0,c.useMemo)((function(){return q(q({},null===W||void 0===W?void 0:W.pipeline),{},{uuid:z})}),[W,z]),$=Z.ZP.pipeline_runs.detail(r.id,{},{refreshInterval:3e3,revalidateOnFocus:!0}).data,Q=(0,c.useMemo)((function(){return(null===$||void 0===$?void 0:$.pipeline_run)||{}}),[$]),ee=Q.block_runs,ne=Q.execution_date,te=Q.id,re=Q.status,ie=(0,s.Db)(Z.ZP.pipeline_runs.useUpdate(te),{onSuccess:function(e){return(0,H.wD)(e,{callback:function(){l(null)},onErrorCallback:function(e,n){return Y({errors:n,response:e})}})}}),ue=(0,i.Z)(ie,2),oe=ue[0],le=ue[1].isLoading,ce=Z.ZP.outputs.block_runs.list(null===o||void 0===o?void 0:o.id),se=ce.data,ae=ce.loading,de=(null===se||void 0===se||null===(n=se.outputs)||void 0===n?void 0:n[0])||{},pe=de.sample_data,fe=de.text_data,ve=de.type;(0,c.useEffect)((function(){o||(null===L||void 0===L?void 0:L.uuid)!==U.uuid||G(M)}),[o,null===L||void 0===L?void 0:L.uuid]);var be=(0,c.useMemo)((function(){return ee||[]}),[Q]),he=((null===pe||void 0===pe?void 0:pe.columns)||[]).slice(0,40),je=(null===pe||void 0===pe?void 0:pe.rows)||[],Oe=(0,c.useMemo)((function(){return(0,R.jsx)(a.Z,{blockRuns:be,onClickRow:function(e){return l((function(n){var t=be[e];return(null===n||void 0===n?void 0:n.id)!==t.id?t:null}))},pipeline:X,selectedRun:o})}),[be,X,o]),ge=(null===X||void 0===X?void 0:X.type)!==O.qL.STREAMING&&re&&re!==j.VO.COMPLETED,me=((null===X||void 0===X?void 0:X.type)===O.qL.PYTHON||(null===X||void 0===X?void 0:X.type)===O.qL.INTEGRATION)&&o&&j.Az.includes(re);return(0,R.jsxs)(h.Z,{breadcrumbs:[{label:function(){return"Runs"},linkProps:{as:"/pipelines/".concat(z,"/runs"),href:"/pipelines/[pipeline]/runs"}},{label:function(){return ne}}],buildSidekick:function(e){return function(e){var n=e.blockRuns,t=e.columns,r=e.dataType,i=e.height,u=e.heightOffset,o=e.loadingData,l=e.pipeline,c=e.renderColumnHeader,s=e.rows,a=e.selectedRun,d=e.selectedTab,p=e.setSelectedTab,f=e.textData,b=A({},(0,P.Z)(e,S));b.blockStatus=(0,C.IJ)(n);var h=(0,R.jsx)(m.Z,{ml:2,children:(0,R.jsx)(y.ZP,{children:"This block run has no output."})}),j=s&&s.length>0?(0,R.jsx)(D.Z,{columnHeaderHeight:c?T.Eh:0,columns:t,height:i-u-90,noBorderBottom:!0,noBorderLeft:!0,noBorderRight:!0,renderColumnHeader:c,rows:s}):h,O=(0,I.Pb)(f)?JSON.stringify(JSON.parse(f),null,2):f,g=f?(0,R.jsx)(m.Z,{ml:2,children:(0,R.jsx)(y.ZP,{monospace:!0,children:(0,R.jsx)("pre",{children:O})})}):h,Z=d&&p;return(0,R.jsxs)(R.Fragment,{children:[(0,R.jsx)("div",{style:{position:"fixed",top:"50px"},children:Z&&(0,R.jsx)(m.Z,{py:E.cd,children:(0,R.jsx)(_.Z,{onClickTab:p,selectedTabUUID:null===d||void 0===d?void 0:d.uuid,tabs:a?F:F.slice(0,1)})})}),(0,R.jsxs)("div",{style:{position:"relative",top:"75px"},children:[(!a||M.uuid===(null===d||void 0===d?void 0:d.uuid))&&(0,R.jsx)(k.Z,A(A({},b),{},{height:i,heightOffset:(u||0)+(Z?N.u$:0),pipeline:l})),a&&U.uuid===(null===d||void 0===d?void 0:d.uuid)&&(0,R.jsxs)(R.Fragment,{children:[o&&(0,R.jsx)(m.Z,{mt:2,children:(0,R.jsx)(v.Z,{alignItems:"center",fullWidth:!0,justifyContent:"center",children:(0,R.jsx)(x.Z,{color:"white",large:!0})})}),!o&&r===w.Gi.TABLE&&j,!o&&r!==w.Gi.TABLE&&g]})]})]})}(q(q({},e),{},{blockRuns:be,columns:he,dataType:ve,loadingData:ae,rows:je,selectedRun:o,selectedTab:L,setSelectedTab:G,showDynamicBlocks:!0,textData:fe}))},errors:K,pageName:B.M.RUNS,pipeline:X,setErrors:Y,subheader:(ge||me)&&(0,R.jsxs)(v.Z,{alignItems:"center",children:[j.BF.includes(re)&&(0,R.jsxs)(f.Z,{children:[(0,R.jsx)(y.ZP,{bold:!0,default:!0,large:!0,children:"Pipeline is running"}),(0,R.jsx)(m.Z,{mr:1}),(0,R.jsx)(x.Z,{inverted:!0}),(0,R.jsx)(m.Z,{mr:2})]}),ge&&(0,R.jsxs)(R.Fragment,{children:[(0,R.jsx)(d.Z,{danger:!0,loading:le,onClick:function(e){(0,V.j)(e),oe({pipeline_run:{pipeline_run_action:"retry_blocks"}})},outline:!0,children:"Retry incomplete blocks"}),(0,R.jsx)(m.Z,{mr:2})]}),me&&(0,R.jsxs)(d.Z,{loading:le,onClick:function(e){(0,V.j)(e),oe({pipeline_run:{from_block_uuid:o.block_uuid,pipeline_run_action:"retry_blocks"}})},outline:!0,primary:!0,children:["Retry from selected block (",o.block_uuid,")"]})]}),title:function(e){var n=e.name;return"".concat(n," runs")},uuid:"".concat(B.M.RUNS,"_").concat(z,"_").concat(te),children:[(0,R.jsx)(m.Z,{mt:E.cd,px:E.cd,children:(0,R.jsx)(b.Z,{level:5,children:"Block runs"})}),(0,R.jsx)(p.Z,{light:!0,mt:E.cd,short:!0}),Oe]})}J.getInitialProps=function(){var e=(0,r.Z)(l().mark((function e(n){var t,r,i;return l().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=n.query,r=t.pipeline,i=t.run,e.abrupt("return",{pipeline:{uuid:r},pipelineRun:{id:i}});case 2:case"end":return e.stop()}}),e)})));return function(n){return e.apply(this,arguments)}}();var K=(0,g.Z)(J)},39525:function(e,n,t){(window.__NEXT_P=window.__NEXT_P||[]).push(["/pipelines/[pipeline]/runs/[run]",function(){return t(23588)}])}},function(e){e.O(0,[844,7607,5896,4804,1774,9350,5872,2125,1424,1005,8180,547,8957,1286,5682,9774,2888,179],(function(){return n=39525,e(e.s=n);var n}));var n=e.O();_N_E=n}]);
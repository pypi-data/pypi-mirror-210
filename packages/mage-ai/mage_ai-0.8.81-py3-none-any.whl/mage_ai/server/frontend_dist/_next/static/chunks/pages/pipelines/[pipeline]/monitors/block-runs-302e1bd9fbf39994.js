(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[5912],{44162:function(n,t,e){"use strict";e.d(t,{HC:function(){return T},Kf:function(){return s},Nk:function(){return p},PY:function(){return f},gE:function(){return A},jv:function(){return m},nz:function(){return b},oh:function(){return d},qn:function(){return l},t1:function(){return h},y9:function(){return R}});var r=e(9518),o=e(23831),i=e(86422),c=e(73942),u=e(49125),a=e(90880),d=68;function l(n,t){var e,r,c=((null===t||void 0===t||null===(e=t.theme)||void 0===e?void 0:e.borders)||o.Z.borders).light,u=((null===t||void 0===t||null===(r=t.theme)||void 0===r?void 0:r.monotone)||o.Z.monotone).grey500,a=t||{},d=a.blockColor,l=a.isSelected,s=a.theme;return l?c=(s||o.Z).content.active:i.tf.TRANSFORMER===n||d===i.Lq.PURPLE?(c=(s||o.Z).accent.purple,u=(s||o.Z).accent.purpleLight):i.tf.DATA_EXPORTER===n||d===i.Lq.YELLOW?(c=(s||o.Z).accent.yellow,u=(s||o.Z).accent.yellowLight):i.tf.DATA_LOADER===n||d===i.Lq.BLUE?(c=(s||o.Z).accent.blue,u=(s||o.Z).accent.blueLight):i.tf.MARKDOWN===n?(c=(s||o.Z).accent.sky,u=(s||o.Z).accent.skyLight):i.tf.SENSOR===n||d===i.Lq.PINK?(c=(s||o.Z).accent.pink,u=(s||o.Z).accent.pinkLight):i.tf.DBT===n?(c=(s||o.Z).accent.dbt,u=(s||o.Z).accent.dbtLight):i.tf.EXTENSION===n||d===i.Lq.TEAL?(c=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).teal,u=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).tealLight):i.tf.CALLBACK===n?(c=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).rose,u=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).roseLight):(i.tf.SCRATCHPAD===n||d===i.Lq.GREY||i.tf.CUSTOM===n&&!d)&&(c=(s||o.Z).content.default,u=(s||o.Z).accent.contentDefaultTransparent),{accent:c,accentLight:u}}var s=(0,r.css)([""," "," "," "," "," "," ",""],(0,a.eR)(),(function(n){return!n.selected&&!n.hasError&&"\n    border-color: ".concat(l(n.blockType,n).accentLight,";\n  ")}),(function(n){return n.selected&&!n.hasError&&"\n    border-color: ".concat(l(n.blockType,n).accent,";\n  ")}),(function(n){return!n.selected&&n.hasError&&"\n    border-color: ".concat((n.theme.accent||o.Z.accent).negativeTransparent,";\n  ")}),(function(n){return n.selected&&n.hasError&&"\n    border-color: ".concat((n.theme.borders||o.Z.borders).danger,";\n  ")}),(function(n){return n.dynamicBlock&&"\n    border-style: dashed !important;\n  "}),(function(n){return n.dynamicChildBlock&&"\n    border-style: dotted !important;\n  "})),p=r.default.div.withConfig({displayName:"indexstyle__ContainerStyle",componentId:"sc-s5rj34-0"})(["border-radius:","px;position:relative;"],c.n_),f=r.default.div.withConfig({displayName:"indexstyle__HiddenBlockContainerStyle",componentId:"sc-s5rj34-1"})([""," border-radius:","px;border-style:",";border-width:","px;",""],s,c.n_,c.M8,c.mP,(function(n){return"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n\n    &:hover {\n      border-color: ").concat(l(n.blockType,n).accent,";\n    }\n  ")})),b=r.default.div.withConfig({displayName:"indexstyle__BlockHeaderStyle",componentId:"sc-s5rj34-2"})([""," border-top-left-radius:","px;border-top-right-radius:","px;border-top-style:",";border-top-width:","px;border-left-style:",";border-left-width:","px;border-right-style:",";border-right-width:","px;padding:","px;position:sticky;top:-5px;"," "," ",""],s,c.n_,c.n_,c.M8,c.mP,c.M8,c.mP,c.M8,c.mP,u.iI,(function(n){return"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n  ")}),(function(n){return n.bottomBorder&&"\n    border-bottom: ".concat(c.YF,"px ").concat(c.M8," ").concat((n.theme||o.Z).borders.medium2,";\n  ")}),(function(n){return n.zIndex&&"\n    z-index: ".concat(6+(n.zIndex||0),";\n  ")})),m=r.default.div.withConfig({displayName:"indexstyle__CodeContainerStyle",componentId:"sc-s5rj34-3"})([""," border-left-style:",";border-left-width:","px;border-right-style:",";border-right-width:","px;padding-bottom:","px;padding-top:","px;position:relative;"," "," "," .line-numbers{opacity:0;}&.selected{.line-numbers{opacity:1 !important;}}"],s,c.M8,c.mP,c.M8,c.mP,u.iI,u.iI,(function(n){return"\n    background-color: ".concat((n.theme.background||o.Z.background).codeTextarea,";\n  ")}),(function(n){return n.lightBackground&&"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n  ")}),(function(n){return!n.hasOutput&&"\n    border-bottom-left-radius: ".concat(c.n_,"px;\n    border-bottom-right-radius: ").concat(c.n_,"px;\n    border-bottom-style: ").concat(c.M8,";\n    border-bottom-width: ").concat(c.mP,"px;\n  ")})),A=r.default.div.withConfig({displayName:"indexstyle__BlockDivider",componentId:"sc-s5rj34-4"})(["align-items:center;display:flex;height:","px;justify-content:center;position:relative;z-index:8;bottom:","px;&:hover{"," .block-divider-inner{","}}"],2*u.iI,.5*u.iI,(function(n){return n.additionalZIndex>0&&"\n      z-index: ".concat(8+n.additionalZIndex,";\n    ")}),(function(n){return"\n        background-color: ".concat((n.theme.text||o.Z.text).fileBrowser,";\n      ")})),h=r.default.div.withConfig({displayName:"indexstyle__BlockDividerInner",componentId:"sc-s5rj34-5"})(["height 1px;width:100%;position:absolute;z-index:-1;top:","px;"],1.5*u.iI),R=r.default.div.withConfig({displayName:"indexstyle__CodeHelperStyle",componentId:"sc-s5rj34-6"})(["margin-bottom:","px;padding-bottom:","px;",""],u.cd*u.iI,u.iI,(function(n){return"\n    border-bottom: 1px solid ".concat((n.theme.borders||o.Z.borders).medium,";\n    padding-left: ").concat(n.normalPadding?u.iI:d,"px;\n  ")})),T=r.default.div.withConfig({displayName:"indexstyle__TimeTrackerStyle",componentId:"sc-s5rj34-7"})(["bottom:","px;left:","px;position:absolute;"],1*u.iI,d)},43032:function(n,t,e){"use strict";e.d(t,{Cl:function(){return u},Nk:function(){return a},ZG:function(){return c}});var r=e(9518),o=e(23831),i=e(49125),c=1.5*i.iI,u=1*c+i.iI/2,a=r.default.div.withConfig({displayName:"indexstyle__ContainerStyle",componentId:"sc-uvd91-0"})([".row:hover{","}"],(function(n){return"\n      background-color: ".concat((n.theme.interactive||o.Z.interactive).hoverBackground,";\n    ")}))},86422:function(n,t,e){"use strict";e.d(t,{$W:function(){return f},DA:function(){return p},HX:function(){return A},J8:function(){return m},L8:function(){return c},Lq:function(){return l},Qj:function(){return h},Ut:function(){return O},V4:function(){return E},VZ:function(){return b},dO:function(){return s},f2:function(){return T},iZ:function(){return R},t6:function(){return u},tf:function(){return d}});var r,o,i,c,u,a=e(82394);!function(n){n.DYNAMIC="dynamic",n.DYNAMIC_CHILD="dynamic_child",n.REDUCE_OUTPUT="reduce_output"}(c||(c={})),function(n){n.MARKDOWN="markdown",n.PYTHON="python",n.R="r",n.SQL="sql",n.YAML="yaml"}(u||(u={}));var d,l,s=(r={},(0,a.Z)(r,u.MARKDOWN,"MD"),(0,a.Z)(r,u.PYTHON,"PY"),(0,a.Z)(r,u.R,"R"),(0,a.Z)(r,u.SQL,"SQL"),(0,a.Z)(r,u.YAML,"YAML"),r);!function(n){n.CALLBACK="callback",n.CHART="chart",n.CUSTOM="custom",n.DATA_EXPORTER="data_exporter",n.DATA_LOADER="data_loader",n.DBT="dbt",n.EXTENSION="extension",n.SCRATCHPAD="scratchpad",n.SENSOR="sensor",n.MARKDOWN="markdown",n.TRANSFORMER="transformer"}(d||(d={})),function(n){n.BLUE="blue",n.GREY="grey",n.PINK="pink",n.PURPLE="purple",n.TEAL="teal",n.YELLOW="yellow"}(l||(l={}));var p,f=[d.CHART,d.CUSTOM,d.DATA_EXPORTER,d.DATA_LOADER,d.SCRATCHPAD,d.SENSOR,d.MARKDOWN,d.TRANSFORMER],b=[d.DATA_EXPORTER,d.DATA_LOADER],m=[d.DATA_EXPORTER,d.DATA_LOADER,d.TRANSFORMER],A=[d.DATA_EXPORTER,d.DATA_LOADER,d.DBT,d.TRANSFORMER],h=[d.CHART,d.SCRATCHPAD,d.SENSOR,d.MARKDOWN],R=[d.CALLBACK,d.CHART,d.EXTENSION,d.SCRATCHPAD,d.MARKDOWN];!function(n){n.EXECUTED="executed",n.FAILED="failed",n.NOT_EXECUTED="not_executed",n.UPDATED="updated"}(p||(p={}));var T=[d.CUSTOM,d.DATA_EXPORTER,d.DATA_LOADER,d.TRANSFORMER],E=(o={},(0,a.Z)(o,d.EXTENSION,"Callback"),(0,a.Z)(o,d.CUSTOM,"Custom"),(0,a.Z)(o,d.DATA_EXPORTER,"Data exporter"),(0,a.Z)(o,d.DATA_LOADER,"Data loader"),(0,a.Z)(o,d.EXTENSION,"Extension"),(0,a.Z)(o,d.SCRATCHPAD,"Scratchpad"),(0,a.Z)(o,d.SENSOR,"Sensor"),(0,a.Z)(o,d.MARKDOWN,"Markdown"),(0,a.Z)(o,d.TRANSFORMER,"Transformer"),o),O=[d.DATA_LOADER,d.TRANSFORMER,d.DATA_EXPORTER,d.SENSOR];i={},(0,a.Z)(i,d.DATA_EXPORTER,"DE"),(0,a.Z)(i,d.DATA_LOADER,"DL"),(0,a.Z)(i,d.SCRATCHPAD,"SP"),(0,a.Z)(i,d.SENSOR,"SR"),(0,a.Z)(i,d.MARKDOWN,"MD"),(0,a.Z)(i,d.TRANSFORMER,"TF")},50094:function(n,t,e){"use strict";e.r(t);var r=e(77837),o=e(75582),i=e(82394),c=e(38860),u=e.n(c),a=e(82684),d=e(92083),l=e.n(d),s=e(9518),p=e(21679),f=e(16634),b=e(67971),m=e(87372),A=e(87465),h=e(41788),R=e(55378),T=e(86673),E=e(82531),O=e(23831),v=e(67400),_=e(43032),Z=e(92953),D=e(44162),g=e(24224),x=e(28598);function y(n,t){var e=Object.keys(n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(n);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(n,t).enumerable}))),e.push.apply(e,r)}return e}function C(n){for(var t=1;t<arguments.length;t++){var e=null!=arguments[t]?arguments[t]:{};t%2?y(Object(e),!0).forEach((function(t){(0,i.Z)(n,t,e[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(n,Object.getOwnPropertyDescriptors(e)):y(Object(e)).forEach((function(t){Object.defineProperty(n,t,Object.getOwnPropertyDescriptor(e,t))}))}return n}function S(n){var t=n.pipeline,e=(0,a.useContext)(s.ThemeContext),r=(0,a.useState)(null),c=r[0],u=r[1],d=t.uuid,h=E.ZP.pipelines.detail(d,{includes_content:!1,includes_outputs:!1},{revalidateOnFocus:!1}).data,y=(0,a.useMemo)((function(){return C(C({},null===h||void 0===h?void 0:h.pipeline),{},{uuid:d})}),[h,d]),S=E.ZP.pipeline_schedules.pipelines.list(d).data,N=(0,a.useMemo)((function(){return null===S||void 0===S?void 0:S.pipeline_schedules}),[S]),L=(0,a.useMemo)((function(){return(0,g.HK)(null===y||void 0===y?void 0:y.blocks,(function(n){return n.uuid}))||{}}),[y]),P={pipeline_uuid:d};(c||0===c)&&(P.pipeline_schedule_id=Number(c));var k=E.ZP.monitor_stats.detail("block_run_count",P),M=k.data,w=k.mutate,I=((null===M||void 0===M?void 0:M.monitor_stat)||{}).stats,j=(0,a.useMemo)((function(){for(var n=new Date,t=[],e=0;e<90;e++)t.unshift(n.toISOString().split("T")[0]),n.setDate(n.getDate()-1);return t}),[]),B=(0,a.useMemo)((function(){if(I)return Object.entries(I).reduce((function(n,t){var e=(0,o.Z)(t,2),r=e[0],c=e[1].data,u=j.map((function(n){return C({date:n},c[n]||{})}));return C(C({},n),{},(0,i.Z)({},r,u))}),{})}),[j,I]),X=(0,a.useMemo)((function(){var n=[];return n.push({bold:!0,label:function(){return"Monitors"}}),n}),[]);return(0,x.jsx)(A.Z,{breadcrumbs:X,monitorType:Z.a.BLOCK_RUNS,pipeline:y,subheader:(0,x.jsx)(b.Z,{children:(0,x.jsxs)(R.Z,{backgroundColor:O.Z.interactive.defaultBackground,label:"Trigger:",onChange:function(n){var t=n.target.value;"initial"!==t?(u(t),w(t)):(w(),u(null))},value:c||"initial",children:[(0,x.jsx)("option",{value:"initial",children:"All"}),N&&N.map((function(n){return(0,x.jsx)("option",{value:n.id,children:n.name},n.id)}))]})}),children:(0,x.jsx)(T.Z,{mx:2,children:B&&Object.entries(B).map((function(n){var t,r,i=(0,o.Z)(n,2),c=i[0],u=i[1];return(0,x.jsxs)(T.Z,{mt:3,children:[(0,x.jsxs)(b.Z,{alignItems:"center",children:[(0,x.jsx)(T.Z,{mx:1,children:(0,x.jsx)(f.Z,{color:(0,D.qn)(null===(t=L[c])||void 0===t?void 0:t.type,{blockColor:null===(r=L[c])||void 0===r?void 0:r.color,theme:e}).accent,size:_.ZG,square:!0})}),(0,x.jsx)(m.Z,{level:4,children:c})]}),(0,x.jsx)(T.Z,{mt:1,children:(0,x.jsx)(p.Z,{colors:v.BAR_STACK_COLORS,data:u,getXValue:function(n){return n.date},height:200,keys:v.BAR_STACK_STATUSES,margin:{bottom:30,left:35,right:0,top:10},tooltipLeftOffset:Z.C,xLabelFormat:function(n){return l()(n).format("MMM DD")}})})]},c)}))})})}S.getInitialProps=function(){var n=(0,r.Z)(u().mark((function n(t){var e;return u().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return e=t.query.pipeline,n.abrupt("return",{pipeline:{uuid:e}});case 2:case"end":return n.stop()}}),n)})));return function(t){return n.apply(this,arguments)}}(),t.default=(0,h.Z)(S)},83542:function(n,t,e){(window.__NEXT_P=window.__NEXT_P||[]).push(["/pipelines/[pipeline]/monitors/block-runs",function(){return e(50094)}])}},function(n){n.O(0,[844,7607,5896,2714,1424,1005,547,9129,9774,2888,179],(function(){return t=83542,n(n.s=t);var t}));var t=n.O();_N_E=t}]);
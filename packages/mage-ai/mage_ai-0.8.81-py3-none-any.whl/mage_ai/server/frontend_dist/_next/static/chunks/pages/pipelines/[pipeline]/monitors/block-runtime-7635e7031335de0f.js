(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[4947],{44162:function(n,e,t){"use strict";t.d(e,{HC:function(){return y},Kf:function(){return s},Nk:function(){return f},PY:function(){return p},gE:function(){return b},jv:function(){return h},nz:function(){return m},oh:function(){return l},qn:function(){return d},t1:function(){return v},y9:function(){return g}});var r=t(9518),o=t(23831),i=t(86422),c=t(73942),u=t(49125),a=t(90880),l=68;function d(n,e){var t,r,c=((null===e||void 0===e||null===(t=e.theme)||void 0===t?void 0:t.borders)||o.Z.borders).light,u=((null===e||void 0===e||null===(r=e.theme)||void 0===r?void 0:r.monotone)||o.Z.monotone).grey500,a=e||{},l=a.blockColor,d=a.isSelected,s=a.theme;return d?c=(s||o.Z).content.active:i.tf.TRANSFORMER===n||l===i.Lq.PURPLE?(c=(s||o.Z).accent.purple,u=(s||o.Z).accent.purpleLight):i.tf.DATA_EXPORTER===n||l===i.Lq.YELLOW?(c=(s||o.Z).accent.yellow,u=(s||o.Z).accent.yellowLight):i.tf.DATA_LOADER===n||l===i.Lq.BLUE?(c=(s||o.Z).accent.blue,u=(s||o.Z).accent.blueLight):i.tf.MARKDOWN===n?(c=(s||o.Z).accent.sky,u=(s||o.Z).accent.skyLight):i.tf.SENSOR===n||l===i.Lq.PINK?(c=(s||o.Z).accent.pink,u=(s||o.Z).accent.pinkLight):i.tf.DBT===n?(c=(s||o.Z).accent.dbt,u=(s||o.Z).accent.dbtLight):i.tf.EXTENSION===n||l===i.Lq.TEAL?(c=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).teal,u=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).tealLight):i.tf.CALLBACK===n?(c=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).rose,u=((null===s||void 0===s?void 0:s.accent)||o.Z.accent).roseLight):(i.tf.SCRATCHPAD===n||l===i.Lq.GREY||i.tf.CUSTOM===n&&!l)&&(c=(s||o.Z).content.default,u=(s||o.Z).accent.contentDefaultTransparent),{accent:c,accentLight:u}}var s=(0,r.css)([""," "," "," "," "," "," ",""],(0,a.eR)(),(function(n){return!n.selected&&!n.hasError&&"\n    border-color: ".concat(d(n.blockType,n).accentLight,";\n  ")}),(function(n){return n.selected&&!n.hasError&&"\n    border-color: ".concat(d(n.blockType,n).accent,";\n  ")}),(function(n){return!n.selected&&n.hasError&&"\n    border-color: ".concat((n.theme.accent||o.Z.accent).negativeTransparent,";\n  ")}),(function(n){return n.selected&&n.hasError&&"\n    border-color: ".concat((n.theme.borders||o.Z.borders).danger,";\n  ")}),(function(n){return n.dynamicBlock&&"\n    border-style: dashed !important;\n  "}),(function(n){return n.dynamicChildBlock&&"\n    border-style: dotted !important;\n  "})),f=r.default.div.withConfig({displayName:"indexstyle__ContainerStyle",componentId:"sc-s5rj34-0"})(["border-radius:","px;position:relative;"],c.n_),p=r.default.div.withConfig({displayName:"indexstyle__HiddenBlockContainerStyle",componentId:"sc-s5rj34-1"})([""," border-radius:","px;border-style:",";border-width:","px;",""],s,c.n_,c.M8,c.mP,(function(n){return"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n\n    &:hover {\n      border-color: ").concat(d(n.blockType,n).accent,";\n    }\n  ")})),m=r.default.div.withConfig({displayName:"indexstyle__BlockHeaderStyle",componentId:"sc-s5rj34-2"})([""," border-top-left-radius:","px;border-top-right-radius:","px;border-top-style:",";border-top-width:","px;border-left-style:",";border-left-width:","px;border-right-style:",";border-right-width:","px;padding:","px;position:sticky;top:-5px;"," "," ",""],s,c.n_,c.n_,c.M8,c.mP,c.M8,c.mP,c.M8,c.mP,u.iI,(function(n){return"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n  ")}),(function(n){return n.bottomBorder&&"\n    border-bottom: ".concat(c.YF,"px ").concat(c.M8," ").concat((n.theme||o.Z).borders.medium2,";\n  ")}),(function(n){return n.zIndex&&"\n    z-index: ".concat(6+(n.zIndex||0),";\n  ")})),h=r.default.div.withConfig({displayName:"indexstyle__CodeContainerStyle",componentId:"sc-s5rj34-3"})([""," border-left-style:",";border-left-width:","px;border-right-style:",";border-right-width:","px;padding-bottom:","px;padding-top:","px;position:relative;"," "," "," .line-numbers{opacity:0;}&.selected{.line-numbers{opacity:1 !important;}}"],s,c.M8,c.mP,c.M8,c.mP,u.iI,u.iI,(function(n){return"\n    background-color: ".concat((n.theme.background||o.Z.background).codeTextarea,";\n  ")}),(function(n){return n.lightBackground&&"\n    background-color: ".concat((n.theme||o.Z).background.content,";\n  ")}),(function(n){return!n.hasOutput&&"\n    border-bottom-left-radius: ".concat(c.n_,"px;\n    border-bottom-right-radius: ").concat(c.n_,"px;\n    border-bottom-style: ").concat(c.M8,";\n    border-bottom-width: ").concat(c.mP,"px;\n  ")})),b=r.default.div.withConfig({displayName:"indexstyle__BlockDivider",componentId:"sc-s5rj34-4"})(["align-items:center;display:flex;height:","px;justify-content:center;position:relative;z-index:8;bottom:","px;&:hover{"," .block-divider-inner{","}}"],2*u.iI,.5*u.iI,(function(n){return n.additionalZIndex>0&&"\n      z-index: ".concat(8+n.additionalZIndex,";\n    ")}),(function(n){return"\n        background-color: ".concat((n.theme.text||o.Z.text).fileBrowser,";\n      ")})),v=r.default.div.withConfig({displayName:"indexstyle__BlockDividerInner",componentId:"sc-s5rj34-5"})(["height 1px;width:100%;position:absolute;z-index:-1;top:","px;"],1.5*u.iI),g=r.default.div.withConfig({displayName:"indexstyle__CodeHelperStyle",componentId:"sc-s5rj34-6"})(["margin-bottom:","px;padding-bottom:","px;",""],u.cd*u.iI,u.iI,(function(n){return"\n    border-bottom: 1px solid ".concat((n.theme.borders||o.Z.borders).medium,";\n    padding-left: ").concat(n.normalPadding?u.iI:l,"px;\n  ")})),y=r.default.div.withConfig({displayName:"indexstyle__TimeTrackerStyle",componentId:"sc-s5rj34-7"})(["bottom:","px;left:","px;position:absolute;"],1*u.iI,l)},92953:function(n,e,t){"use strict";var r;t.d(e,{C:function(){return o},a:function(){return r}}),function(n){n.BLOCK_RUNS="block_runs",n.BLOCK_RUNTIME="block_runtime",n.PIPELINE_RUNS="pipeline_runs"}(r||(r={}));var o=-50},87465:function(n,e,t){"use strict";t.d(e,{Z:function(){return b}});t(82684);var r=t(34376),o=t(87372),i=t(60547),c=t(86673),u=t(19711),a=t(2850),l=t(9518),d=t(23831),s=t(49125),f=l.default.div.withConfig({displayName:"indexstyle__LinkStyle",componentId:"sc-1in9sst-0"})(["padding:","px ","px;"," ",""],s.iI,s.tr,(function(n){return n.selected&&"\n    background-color: ".concat((n.theme.interactive||d.Z.interactive).checked,";\n  ")}),(function(n){return!n.selected&&"\n    cursor: pointer;\n  "})),p=t(92953),m=t(59920),h=t(28598);var b=function(n){var e=n.breadcrumbs,t=n.children,l=n.errors,d=n.monitorType,b=n.pipeline,v=n.setErrors,g=n.subheader,y=(0,r.useRouter)();return(0,h.jsx)(i.Z,{before:(0,h.jsxs)(a.M,{children:[(0,h.jsx)(c.Z,{p:s.cd,children:(0,h.jsx)(o.Z,{level:4,muted:!0,children:"Insights"})}),(0,h.jsx)(f,{onClick:function(n){n.preventDefault(),y.push("/pipelines/[pipeline]/monitors","/pipelines/".concat(null===b||void 0===b?void 0:b.uuid,"/monitors"))},selected:p.a.PIPELINE_RUNS==d,children:(0,h.jsx)(u.ZP,{children:"Pipeline runs"})}),(0,h.jsx)(f,{onClick:function(n){n.preventDefault(),y.push("/pipelines/[pipeline]/monitors/block-runs","/pipelines/".concat(null===b||void 0===b?void 0:b.uuid,"/monitors/block-runs"))},selected:p.a.BLOCK_RUNS==d,children:(0,h.jsx)(u.ZP,{children:"Block runs"})}),(0,h.jsx)(f,{onClick:function(n){n.preventDefault(),y.push("/pipelines/[pipeline]/monitors/block-runtime","/pipelines/".concat(null===b||void 0===b?void 0:b.uuid,"/monitors/block-runtime"))},selected:p.a.BLOCK_RUNTIME==d,children:(0,h.jsx)(u.ZP,{children:"Block runtime"})})]}),breadcrumbs:e,errors:l,pageName:m.M.MONITOR,pipeline:b,setErrors:v,subheader:g,uuid:"pipeline/monitor",children:t})}},2850:function(n,e,t){"use strict";t.d(e,{M:function(){return c},W:function(){return i}});var r=t(9518),o=t(3055),i=34*t(49125).iI,c=r.default.div.withConfig({displayName:"indexstyle__BeforeStyle",componentId:"sc-12ee2ib-0"})(["min-height:calc(100vh - ","px);"],o.Mz)},45739:function(n,e,t){"use strict";t.d(e,{K:function(){return o}});var r=t(31969),o=function(n){var e=n||r.Z,t=e.brand,o=t.earth200,i=t.earth300,c=t.earth400,u=t.energy200,a=t.energy300,l=t.energy400,d=t.fire200,s=t.fire300,f=t.fire400,p=t.water200,m=t.water300,h=t.water400,b=t.wind200,v=t.wind300,g=t.wind400,y=e.chart;return[y.backgroundPrimary,y.backgroundSecondary,y.backgroundTertiary].concat([g,h,f,l,c,v,m,s,a,i,b,p,d,u,o])}},52359:function(n,e,t){"use strict";var r=t(9518).default.div.withConfig({displayName:"YAxisLabelContainer",componentId:"sc-qwp21x-0"})(["-webkit-transform:rotate(-90deg);-moz-transform:rotate(-90deg);-o-transform:rotate(-90deg);-ms-transform:rotate(-90deg);transform:rotate(-90deg);white-space:nowrap;"]);e.Z=r},344:function(n,e,t){"use strict";t.d(e,{P5:function(){return o},Vs:function(){return i}});t(90211);var r=Intl.NumberFormat("en-US",{notation:"compact",maximumFractionDigits:2});function o(n){return"number"!==typeof n?n:n>=1e4?r.format(n):n.toString()}function i(n,e,t){var r,o;if("undefined"===typeof n||"undefined"===typeof e)return 0;var i=null===n||void 0===n||null===(r=n(e,t))||void 0===r||null===(o=r.props)||void 0===o?void 0:o.children;return(Array.isArray(i)?i:[i]).join("").length}},86422:function(n,e,t){"use strict";t.d(e,{$W:function(){return p},DA:function(){return f},HX:function(){return b},J8:function(){return h},L8:function(){return c},Lq:function(){return d},Qj:function(){return v},Ut:function(){return A},V4:function(){return O},VZ:function(){return m},dO:function(){return s},f2:function(){return y},iZ:function(){return g},t6:function(){return u},tf:function(){return l}});var r,o,i,c,u,a=t(82394);!function(n){n.DYNAMIC="dynamic",n.DYNAMIC_CHILD="dynamic_child",n.REDUCE_OUTPUT="reduce_output"}(c||(c={})),function(n){n.MARKDOWN="markdown",n.PYTHON="python",n.R="r",n.SQL="sql",n.YAML="yaml"}(u||(u={}));var l,d,s=(r={},(0,a.Z)(r,u.MARKDOWN,"MD"),(0,a.Z)(r,u.PYTHON,"PY"),(0,a.Z)(r,u.R,"R"),(0,a.Z)(r,u.SQL,"SQL"),(0,a.Z)(r,u.YAML,"YAML"),r);!function(n){n.CALLBACK="callback",n.CHART="chart",n.CUSTOM="custom",n.DATA_EXPORTER="data_exporter",n.DATA_LOADER="data_loader",n.DBT="dbt",n.EXTENSION="extension",n.SCRATCHPAD="scratchpad",n.SENSOR="sensor",n.MARKDOWN="markdown",n.TRANSFORMER="transformer"}(l||(l={})),function(n){n.BLUE="blue",n.GREY="grey",n.PINK="pink",n.PURPLE="purple",n.TEAL="teal",n.YELLOW="yellow"}(d||(d={}));var f,p=[l.CHART,l.CUSTOM,l.DATA_EXPORTER,l.DATA_LOADER,l.SCRATCHPAD,l.SENSOR,l.MARKDOWN,l.TRANSFORMER],m=[l.DATA_EXPORTER,l.DATA_LOADER],h=[l.DATA_EXPORTER,l.DATA_LOADER,l.TRANSFORMER],b=[l.DATA_EXPORTER,l.DATA_LOADER,l.DBT,l.TRANSFORMER],v=[l.CHART,l.SCRATCHPAD,l.SENSOR,l.MARKDOWN],g=[l.CALLBACK,l.CHART,l.EXTENSION,l.SCRATCHPAD,l.MARKDOWN];!function(n){n.EXECUTED="executed",n.FAILED="failed",n.NOT_EXECUTED="not_executed",n.UPDATED="updated"}(f||(f={}));var y=[l.CUSTOM,l.DATA_EXPORTER,l.DATA_LOADER,l.TRANSFORMER],O=(o={},(0,a.Z)(o,l.EXTENSION,"Callback"),(0,a.Z)(o,l.CUSTOM,"Custom"),(0,a.Z)(o,l.DATA_EXPORTER,"Data exporter"),(0,a.Z)(o,l.DATA_LOADER,"Data loader"),(0,a.Z)(o,l.EXTENSION,"Extension"),(0,a.Z)(o,l.SCRATCHPAD,"Scratchpad"),(0,a.Z)(o,l.SENSOR,"Sensor"),(0,a.Z)(o,l.MARKDOWN,"Markdown"),(0,a.Z)(o,l.TRANSFORMER,"Transformer"),o),A=[l.DATA_LOADER,l.TRANSFORMER,l.DATA_EXPORTER,l.SENSOR];i={},(0,a.Z)(i,l.DATA_EXPORTER,"DE"),(0,a.Z)(i,l.DATA_LOADER,"DL"),(0,a.Z)(i,l.SCRATCHPAD,"SP"),(0,a.Z)(i,l.SENSOR,"SR"),(0,a.Z)(i,l.MARKDOWN,"MD"),(0,a.Z)(i,l.TRANSFORMER,"TF")},34744:function(n,e,t){"use strict";var r=t(82394),o=t(26304),i=(t(82684),t(9518)),c=t(86673),u=t(23831),a=t(49125),l=t(28598),d=["short"];function s(n,e){var t=Object.keys(n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(n);e&&(r=r.filter((function(e){return Object.getOwnPropertyDescriptor(n,e).enumerable}))),t.push.apply(t,r)}return t}function f(n){for(var e=1;e<arguments.length;e++){var t=null!=arguments[e]?arguments[e]:{};e%2?s(Object(t),!0).forEach((function(e){(0,r.Z)(n,e,t[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(n,Object.getOwnPropertyDescriptors(t)):s(Object(t)).forEach((function(e){Object.defineProperty(n,e,Object.getOwnPropertyDescriptor(t,e))}))}return n}var p=i.default.div.withConfig({displayName:"Divider__DividerContainerStyle",componentId:"sc-1m7lqco-0"})([""," ",""],(function(n){return n.short&&"\n    width: ".concat(21*a.iI,"px;\n  ")}),(function(n){return!n.short&&"\n    width: 100%;\n  "})),m=i.default.div.withConfig({displayName:"Divider__DividerStyle",componentId:"sc-1m7lqco-1"})(["height:1px;"," "," "," "," "," ",""],(function(n){return!(n.light||n.medium)&&"\n    background-color: ".concat((n.theme.monotone||u.Z.monotone).grey200,";\n  ")}),(function(n){return n.muted&&"\n    background-color: ".concat((n.theme.monotone||u.Z.monotone).grey500,";\n  ")}),(function(n){return n.light&&"\n    background-color: ".concat((n.theme.borders||u.Z.borders).light,";\n  ")}),(function(n){return n.medium&&"\n    background-color: ".concat((n.theme.borders||u.Z.borders).medium,";\n  ")}),(function(n){return n.prominent&&"\n    background-color: ".concat((n.theme.monotone||u.Z.monotone).grey300,";\n  ")}),(function(n){return n.black&&"\n    background-color: ".concat((n.theme.monotone||u.Z.monotone).black,";\n  ")})),h=function(n){var e=n.short,t=(0,o.Z)(n,d);return(0,l.jsx)(p,{short:e,children:(0,l.jsx)(c.Z,f(f({},t),{},{children:(0,l.jsx)(m,f({},t))}))})};h.defaultProps={short:!1},e.Z=h},68805:function(n,e,t){"use strict";t.r(e);var r=t(77837),o=t(75582),i=t(82394),c=t(38860),u=t.n(c),a=t(82684),l=t(92083),d=t.n(l),s=t(16634),f=t(67971),p=t(87372),m=t(68735),h=t(87465),b=t(41788),v=t(86673),g=t(55378),y=t(19711),O=t(82531),A=t(23831),x=t(73942),R=t(43032),E=t(92953),T=t(9518),Z=t(44162),_=t(24224),k=t(28598);function w(n,e){var t=Object.keys(n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(n);e&&(r=r.filter((function(e){return Object.getOwnPropertyDescriptor(n,e).enumerable}))),t.push.apply(t,r)}return t}function D(n){for(var e=1;e<arguments.length;e++){var t=null!=arguments[e]?arguments[e]:{};e%2?w(Object(t),!0).forEach((function(e){(0,i.Z)(n,e,t[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(n,Object.getOwnPropertyDescriptors(t)):w(Object(t)).forEach((function(e){Object.defineProperty(n,e,Object.getOwnPropertyDescriptor(t,e))}))}return n}function C(n){var e=n.pipeline,t=(0,a.useContext)(T.ThemeContext),r=(0,a.useState)(null),c=r[0],u=r[1],l=e.uuid,b=O.ZP.pipelines.detail(l,{includes_content:!1,includes_outputs:!1},{revalidateOnFocus:!1}).data,w=(0,a.useMemo)((function(){return D(D({},null===b||void 0===b?void 0:b.pipeline),{},{uuid:l})}),[b,l]),C=O.ZP.pipeline_schedules.pipelines.list(l).data,N=(0,a.useMemo)((function(){return null===C||void 0===C?void 0:C.pipeline_schedules}),[C]),S=(0,a.useMemo)((function(){return(0,_.HK)(null===w||void 0===w?void 0:w.blocks,(function(n){return n.uuid}))||{}}),[w]),P={pipeline_uuid:l};(c||0===c)&&(P.pipeline_schedule_id=Number(c));var j=O.ZP.monitor_stats.detail("block_run_time",P),L=j.data,M=j.mutate;(0,a.useEffect)((function(){M(c)}),[M,c]);var I=((null===L||void 0===L?void 0:L.monitor_stat)||{}).stats,B=(0,a.useMemo)((function(){for(var n=new Date,e=[],t=0;t<90;t++)e.unshift(n.toISOString().split("T")[0]),n.setDate(n.getDate()-1);return e}),[]),U=(0,a.useMemo)((function(){if(I)return Object.entries(I).reduce((function(n,e){var t=(0,o.Z)(e,2),r=t[0],c=t[1].data;return D(D({},n),{},(0,i.Z)({},r,B.map((function(n){return{x:n,y:n in c?[c[n]]:null}}))))}),{})}),[I]),X=(0,a.useMemo)((function(){var n=[];return n.push({bold:!0,label:function(){return"Monitors"}}),n}),[w]);return(0,k.jsx)(h.Z,{breadcrumbs:X,monitorType:E.a.BLOCK_RUNTIME,pipeline:w,subheader:(0,k.jsx)(f.Z,{children:(0,k.jsxs)(g.Z,{backgroundColor:A.Z.interactive.defaultBackground,label:"Trigger:",onChange:function(n){var e=n.target.value;"initial"!==e?(u(e),M(e)):(M(),u(null))},value:c||"initial",children:[(0,k.jsx)("option",{value:"initial",children:"All"}),N&&N.map((function(n){return(0,k.jsx)("option",{value:n.id,children:n.name},n.id)}))]})}),children:(0,k.jsx)(v.Z,{mx:2,children:U&&Object.entries(U).map((function(n,e){var r,i,c=(0,o.Z)(n,2),u=c[0],a=c[1];return(0,k.jsxs)(v.Z,{mt:2,children:[(0,k.jsxs)(f.Z,{alignItems:"center",children:[(0,k.jsx)(v.Z,{mx:1,children:(0,k.jsx)(s.Z,{color:(0,Z.qn)(null===(r=S[u])||void 0===r?void 0:r.type,{blockColor:null===(i=S[u])||void 0===i?void 0:i.color,theme:t}).accent,size:R.ZG,square:!0})}),(0,k.jsx)(p.Z,{level:4,children:u})]}),(0,k.jsx)("div",{style:{backgroundColor:A.Z.background.chartBlock,borderRadius:"".concat(x.TR,"px"),marginTop:"8px"},children:(0,k.jsx)(m.Z,{data:a,getX:function(n){return d()(n.x).valueOf()},gridProps:{stroke:"black",strokeDasharray:null,strokeOpacity:.2},height:200,hideGridX:!0,margin:{top:10,bottom:30,left:35,right:-1},noCurve:!0,renderXTooltipContent:function(n){return(0,k.jsx)(y.ZP,{center:!0,inverted:!0,small:!0,children:d()(n.x).format("MMM DD")})},renderYTooltipContent:function(n){var e,t=null===n||void 0===n||null===(e=n.y)||void 0===e?void 0:e[0];return void 0!==t&&(0,k.jsxs)(y.ZP,{center:!0,inverted:!0,small:!0,children:[t.toFixed?t.toFixed(3):t,"s"]})},thickStroke:!0,xLabelFormat:function(n){return d()(n).format("MMM DD")},xLabelRotate:!1})})]},"".concat(u,"_").concat(e))}))})})}C.getInitialProps=function(){var n=(0,r.Z)(u().mark((function n(e){var t;return u().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return t=e.query.pipeline,n.abrupt("return",{pipeline:{uuid:t}});case 2:case"end":return n.stop()}}),n)})));return function(e){return n.apply(this,arguments)}}(),e.default=(0,b.Z)(C)},90211:function(n,e,t){"use strict";t.d(e,{RA:function(){return d},kC:function(){return s},vg:function(){return g},kE:function(){return E},T3:function(){return A},Mp:function(){return f},Pb:function(){return a},HW:function(){return O},wX:function(){return p},x6:function(){return m},_6:function(){return h},zf:function(){return y},Y6:function(){return R},wE:function(){return T},J3:function(){return b},We:function(){return l},QV:function(){return x},C5:function(){return v}});var r=t(75582),o=t(17717),i=["aged","ancient","autumn","billowing","bitter","black","blue","bold","broken","cold","cool","crimson","damp","dark","dawn","delicate","divine","dry","empty","falling","floral","fragrant","frosty","green","hidden","holy","icy","late","lingering","little","lively","long","misty","morning","muddy","nameless","old","patient","polished","proud","purple","quiet","red","restless","rough","shy","silent","small","snowy","solitary","sparkling","spring","still","summer","throbbing","twilight","wandering","weathered","white","wild","winter","wispy","withered","young"],c=(t(92083),["bird","breeze","brook","bush","butterfly","cherry","cloud","darkness","dawn","dew","dream","dust","feather","field","fire","firefly","flower","fog","forest","frog","frost","glade","glitter","grass","haze","hill","lake","leaf","meadow","moon","morning","mountain","night","paper","pine","pond","rain","resonance","river","sea","shadow","shape","silence","sky","smoke","snow","snowflake","sound","star","sun","sun","sunset","surf","thunder","tree","violet","voice","water","water","waterfall","wave","wildflower","wind","wood"]),u=t(24224);function a(n){if(!n)return!1;try{JSON.parse(n)}catch(e){return!1}return!0}function l(n){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"_";return n.split(" ").join(e)}function d(n){return n.split(" ").join("_")}function s(n){return n?n.charAt(0).toUpperCase()+n.slice(1):""}function f(){var n=arguments.length>0&&void 0!==arguments[0]?arguments[0]:1;return String((new Date).getTime()*n)}function p(n){return n.charAt(0).toLowerCase()+n.slice(1)}function m(n){if(null===n||"undefined"===typeof n)return"";var e=n.toString().split("."),t=(0,r.Z)(e,2),o=t[0],i=t[1],c=o.toString().replace(/\B(?=(\d{3})+(?!\d))/g,",");return i?"".concat(c,".").concat(i):c}function h(n,e){var t,r=arguments.length>2&&void 0!==arguments[2]&&arguments[2],o=e,i=void 0!==o&&null!==o;if(i||(o=2),1===o)t=n;else{var c=n.length,u=n[c-1];t="y"===u&&"day"!==n?"".concat(n.slice(0,c-1),"ies"):"".concat(n,"s"===u?"es":"s")}if(i){var a=r?m(o):o;return"".concat(a," ").concat(t)}return t}function b(n){return null===n||void 0===n?void 0:n.replace(/_/g," ")}function v(n){var e=n.length;return"ies"===n.slice(e-3,e)?"".concat(n.slice(0,e-3),"y"):"es"===n.slice(e-2,e)&&"ces"!==n.slice(e-3,e)?n.slice(0,e-2):n.slice(0,e-1)}function g(){var n=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return s(b(n.toLowerCase()))}function y(n){var e,t=[["second",60],["minute",60],["hour",24],["day",7],["week",4],["month",12],["year",null]];return t.forEach((function(o,i){if(!e){var c=(0,r.Z)(o,2),u=c[0],a=c[1],l=t.slice(0,i).reduce((function(n,e){return n*Number(e[1])}),1);n<Number(a)*l&&(e=h(u,Math.round(n/l)))}})),e}function O(n){return!isNaN(n)}function A(n){return"".concat(m(function(n){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:2;return Math.round((n||0)*Math.pow(100,e))/100}(n)),"%")}function x(n){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:2,t=Math.pow(10,e);return Math.round((n||0)*t)/t}function R(){return"".concat((0,u.mp)(i)," ").concat((0,u.mp)(c))}function E(n){return null===n||void 0===n?void 0:n.toLowerCase().replace(/\W+/g,"_")}function T(n){var e,t=n.split(o.sep),r=t[t.length-1].split(".");return e=1===r.length?r[0]:r.slice(0,-1).join("."),t.slice(0,t.length-1).concat(e).join(o.sep)}},76017:function(n,e,t){(window.__NEXT_P=window.__NEXT_P||[]).push(["/pipelines/[pipeline]/monitors/block-runtime",function(){return t(68805)}])}},function(n){n.O(0,[3662,844,7607,5896,2714,9832,1424,1005,547,6567,9774,2888,179],(function(){return e=76017,n(n.s=e);var e}));var e=n.O();_N_E=e}]);
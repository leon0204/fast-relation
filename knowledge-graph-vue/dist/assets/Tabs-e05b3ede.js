import{cN as ct,cO as bt,d as K,cP as ue,m as z,cQ as ft,cR as pt,h as l,c as ut,p as ye,c4 as vt,q as Y,bL as ht,F as gt,N as xt,cS as mt,cI as yt,cT as wt,f as r,c6 as o,e as u,a3 as W,k as St,s as Ct,u as we,cU as ve,cL as Z,ca as Rt,w as ee,H as zt,J as Tt,l as B,cV as $t,I as Pt,v as Wt,cv as he,cK as te,cg as U,cW as Lt,ao as ae,y as _t,A as At,cX as Bt,cM as Et,cY as jt,a9 as E,cZ as G}from"./index-4af02034.js";import{A as kt}from"./Add-5786f0d6.js";var Ht="Expected a function";function re(e,i,c){var v=!0,d=!0;if(typeof e!="function")throw new TypeError(Ht);return ct(c)&&(v="leading"in c?!!c.leading:v,d="trailing"in c?!!c.trailing:d),bt(e,i,{leading:v,maxWait:i,trailing:d})}const Ot=ue(".v-x-scroll",{overflow:"auto",scrollbarWidth:"none"},[ue("&::-webkit-scrollbar",{width:0,height:0})]),Ft=K({name:"XScroll",props:{disabled:Boolean,onScroll:Function},setup(){const e=z(null);function i(d){!(d.currentTarget.offsetWidth<d.currentTarget.scrollWidth)||d.deltaY===0||(d.currentTarget.scrollLeft+=d.deltaY+d.deltaX,d.preventDefault())}const c=ft();return Ot.mount({id:"vueuc/x-scroll",head:!0,anchorMetaName:pt,ssr:c}),Object.assign({selfRef:e,handleWheel:i},{scrollTo(...d){var y;(y=e.value)===null||y===void 0||y.scrollTo(...d)}})},render(){return l("div",{ref:"selfRef",onScroll:this.onScroll,onWheel:this.disabled?void 0:this.handleWheel,class:"v-x-scroll"},this.$slots)}}),ie=ut("n-tabs"),Se={tab:[String,Number,Object,Function],name:{type:[String,Number],required:!0},disabled:Boolean,displayDirective:{type:String,default:"if"},closable:{type:Boolean,default:void 0},tabProps:Object,label:[String,Number,Object,Function]},Xt=K({__TAB_PANE__:!0,name:"TabPane",alias:["TabPanel"],props:Se,setup(e){const i=ye(ie,null);return i||vt("tab-pane","`n-tab-pane` must be placed inside `n-tabs`."),{style:i.paneStyleRef,class:i.paneClassRef,mergedClsPrefix:i.mergedClsPrefixRef}},render(){return l("div",{class:[`${this.mergedClsPrefix}-tab-pane`,this.class],style:this.style},this.$slots)}}),It=Object.assign({internalLeftPadded:Boolean,internalAddable:Boolean,internalCreatedByPane:Boolean},wt(Se,["displayDirective"])),oe=K({__TAB__:!0,inheritAttrs:!1,name:"Tab",props:It,setup(e){const{mergedClsPrefixRef:i,valueRef:c,typeRef:v,closableRef:d,tabStyleRef:y,addTabStyleRef:h,tabClassRef:w,addTabClassRef:S,tabChangeIdRef:g,onBeforeLeaveRef:f,triggerRef:j,handleAdd:_,activateTab:x,handleClose:C}=ye(ie);return{trigger:j,mergedClosable:Y(()=>{if(e.internalAddable)return!1;const{closable:m}=e;return m===void 0?d.value:m}),style:y,addStyle:h,tabClass:w,addTabClass:S,clsPrefix:i,value:c,type:v,handleClose(m){m.stopPropagation(),!e.disabled&&C(e.name)},activateTab(){if(e.disabled)return;if(e.internalAddable){_();return}const{name:m}=e,$=++g.id;if(m!==c.value){const{value:A}=f;A?Promise.resolve(A(e.name,c.value)).then(T=>{T&&g.id===$&&x(m)}):x(m)}}}},render(){const{internalAddable:e,clsPrefix:i,name:c,disabled:v,label:d,tab:y,value:h,mergedClosable:w,trigger:S,$slots:{default:g}}=this,f=d!=null?d:y;return l("div",{class:`${i}-tabs-tab-wrapper`},this.internalLeftPadded?l("div",{class:`${i}-tabs-tab-pad`}):null,l("div",Object.assign({key:c,"data-name":c,"data-disabled":v?!0:void 0},ht({class:[`${i}-tabs-tab`,h===c&&`${i}-tabs-tab--active`,v&&`${i}-tabs-tab--disabled`,w&&`${i}-tabs-tab--closable`,e&&`${i}-tabs-tab--addable`,e?this.addTabClass:this.tabClass],onClick:S==="click"?this.activateTab:void 0,onMouseenter:S==="hover"?this.activateTab:void 0,style:e?this.addStyle:this.style},this.internalCreatedByPane?this.tabProps||{}:this.$attrs)),l("span",{class:`${i}-tabs-tab__label`},e?l(gt,null,l("div",{class:`${i}-tabs-tab__height-placeholder`}," "),l(xt,{clsPrefix:i},{default:()=>l(kt,null)})):g?g():typeof f=="object"?f:mt(f!=null?f:c)),w&&this.type==="card"?l(yt,{clsPrefix:i,class:`${i}-tabs-tab__close`,onClick:this.handleClose,disabled:v}):null))}}),Dt=r("tabs",`
 box-sizing: border-box;
 width: 100%;
 display: flex;
 flex-direction: column;
 transition:
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
`,[o("segment-type",[r("tabs-rail",[u("&.transition-disabled",[r("tabs-capsule",`
 transition: none;
 `)])])]),o("top",[r("tab-pane",`
 padding: var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left);
 `)]),o("left",[r("tab-pane",`
 padding: var(--n-pane-padding-right) var(--n-pane-padding-bottom) var(--n-pane-padding-left) var(--n-pane-padding-top);
 `)]),o("left, right",`
 flex-direction: row;
 `,[r("tabs-bar",`
 width: 2px;
 right: 0;
 transition:
 top .2s var(--n-bezier),
 max-height .2s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),r("tabs-tab",`
 padding: var(--n-tab-padding-vertical); 
 `)]),o("right",`
 flex-direction: row-reverse;
 `,[r("tab-pane",`
 padding: var(--n-pane-padding-left) var(--n-pane-padding-top) var(--n-pane-padding-right) var(--n-pane-padding-bottom);
 `),r("tabs-bar",`
 left: 0;
 `)]),o("bottom",`
 flex-direction: column-reverse;
 justify-content: flex-end;
 `,[r("tab-pane",`
 padding: var(--n-pane-padding-bottom) var(--n-pane-padding-right) var(--n-pane-padding-top) var(--n-pane-padding-left);
 `),r("tabs-bar",`
 top: 0;
 `)]),r("tabs-rail",`
 position: relative;
 padding: 3px;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 background-color: var(--n-color-segment);
 transition: background-color .3s var(--n-bezier);
 display: flex;
 align-items: center;
 `,[r("tabs-capsule",`
 border-radius: var(--n-tab-border-radius);
 position: absolute;
 pointer-events: none;
 background-color: var(--n-tab-color-segment);
 box-shadow: 0 1px 3px 0 rgba(0, 0, 0, .08);
 transition: transform 0.3s var(--n-bezier);
 `),r("tabs-tab-wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[r("tabs-tab",`
 overflow: hidden;
 border-radius: var(--n-tab-border-radius);
 width: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 `,[o("active",`
 font-weight: var(--n-font-weight-strong);
 color: var(--n-tab-text-color-active);
 `),u("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])])]),o("flex",[r("tabs-nav",`
 width: 100%;
 position: relative;
 `,[r("tabs-wrapper",`
 width: 100%;
 `,[r("tabs-tab",`
 margin-right: 0;
 `)])])]),r("tabs-nav",`
 box-sizing: border-box;
 line-height: 1.5;
 display: flex;
 transition: border-color .3s var(--n-bezier);
 `,[W("prefix, suffix",`
 display: flex;
 align-items: center;
 `),W("prefix","padding-right: 16px;"),W("suffix","padding-left: 16px;")]),o("top, bottom",[r("tabs-nav-scroll-wrapper",[u("&::before",`
 top: 0;
 bottom: 0;
 left: 0;
 width: 20px;
 `),u("&::after",`
 top: 0;
 bottom: 0;
 right: 0;
 width: 20px;
 `),o("shadow-start",[u("&::before",`
 box-shadow: inset 10px 0 8px -8px rgba(0, 0, 0, .12);
 `)]),o("shadow-end",[u("&::after",`
 box-shadow: inset -10px 0 8px -8px rgba(0, 0, 0, .12);
 `)])])]),o("left, right",[r("tabs-nav-scroll-content",`
 flex-direction: column;
 `),r("tabs-nav-scroll-wrapper",[u("&::before",`
 top: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),u("&::after",`
 bottom: 0;
 left: 0;
 right: 0;
 height: 20px;
 `),o("shadow-start",[u("&::before",`
 box-shadow: inset 0 10px 8px -8px rgba(0, 0, 0, .12);
 `)]),o("shadow-end",[u("&::after",`
 box-shadow: inset 0 -10px 8px -8px rgba(0, 0, 0, .12);
 `)])])]),r("tabs-nav-scroll-wrapper",`
 flex: 1;
 position: relative;
 overflow: hidden;
 `,[r("tabs-nav-y-scroll",`
 height: 100%;
 width: 100%;
 overflow-y: auto; 
 scrollbar-width: none;
 `,[u("&::-webkit-scrollbar",`
 width: 0;
 height: 0;
 `)]),u("&::before, &::after",`
 transition: box-shadow .3s var(--n-bezier);
 pointer-events: none;
 content: "";
 position: absolute;
 z-index: 1;
 `)]),r("tabs-nav-scroll-content",`
 display: flex;
 position: relative;
 min-width: 100%;
 min-height: 100%;
 width: fit-content;
 box-sizing: border-box;
 `),r("tabs-wrapper",`
 display: inline-flex;
 flex-wrap: nowrap;
 position: relative;
 `),r("tabs-tab-wrapper",`
 display: flex;
 flex-wrap: nowrap;
 flex-shrink: 0;
 flex-grow: 0;
 `),r("tabs-tab",`
 cursor: pointer;
 white-space: nowrap;
 flex-wrap: nowrap;
 display: inline-flex;
 align-items: center;
 color: var(--n-tab-text-color);
 font-size: var(--n-tab-font-size);
 background-clip: padding-box;
 padding: var(--n-tab-padding);
 transition:
 box-shadow .3s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `,[o("disabled",{cursor:"not-allowed"}),W("close",`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `),W("label",`
 display: flex;
 align-items: center;
 z-index: 1;
 `)]),r("tabs-bar",`
 position: absolute;
 bottom: 0;
 height: 2px;
 border-radius: 1px;
 background-color: var(--n-bar-color);
 transition:
 left .2s var(--n-bezier),
 max-width .2s var(--n-bezier),
 opacity .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `,[u("&.transition-disabled",`
 transition: none;
 `),o("disabled",`
 background-color: var(--n-tab-text-color-disabled)
 `)]),r("tabs-pane-wrapper",`
 position: relative;
 overflow: hidden;
 transition: max-height .2s var(--n-bezier);
 `),r("tab-pane",`
 color: var(--n-pane-text-color);
 width: 100%;
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 opacity .2s var(--n-bezier);
 left: 0;
 right: 0;
 top: 0;
 `,[u("&.next-transition-leave-active, &.prev-transition-leave-active, &.next-transition-enter-active, &.prev-transition-enter-active",`
 transition:
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 transform .2s var(--n-bezier),
 opacity .2s var(--n-bezier);
 `),u("&.next-transition-leave-active, &.prev-transition-leave-active",`
 position: absolute;
 `),u("&.next-transition-enter-from, &.prev-transition-leave-to",`
 transform: translateX(32px);
 opacity: 0;
 `),u("&.next-transition-leave-to, &.prev-transition-enter-from",`
 transform: translateX(-32px);
 opacity: 0;
 `),u("&.next-transition-leave-from, &.next-transition-enter-to, &.prev-transition-leave-from, &.prev-transition-enter-to",`
 transform: translateX(0);
 opacity: 1;
 `)]),r("tabs-tab-pad",`
 box-sizing: border-box;
 width: var(--n-tab-gap);
 flex-grow: 0;
 flex-shrink: 0;
 `),o("line-type, bar-type",[r("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 box-sizing: border-box;
 vertical-align: bottom;
 `,[u("&:hover",{color:"var(--n-tab-text-color-hover)"}),o("active",`
 color: var(--n-tab-text-color-active);
 font-weight: var(--n-tab-font-weight-active);
 `),o("disabled",{color:"var(--n-tab-text-color-disabled)"})])]),r("tabs-nav",[o("line-type",[o("top",[W("prefix, suffix",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 bottom: -1px;
 `)]),o("left",[W("prefix, suffix",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 right: -1px;
 `)]),o("right",[W("prefix, suffix",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 left: -1px;
 `)]),o("bottom",[W("prefix, suffix",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-nav-scroll-content",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-bar",`
 top: -1px;
 `)]),W("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-nav-scroll-content",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-bar",`
 border-radius: 0;
 `)]),o("card-type",[W("prefix, suffix",`
 transition: border-color .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 flex-grow: 1;
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-tab-pad",`
 transition: border-color .3s var(--n-bezier);
 `),r("tabs-tab",`
 font-weight: var(--n-tab-font-weight);
 border: 1px solid var(--n-tab-border-color);
 background-color: var(--n-tab-color);
 box-sizing: border-box;
 position: relative;
 vertical-align: bottom;
 display: flex;
 justify-content: space-between;
 font-size: var(--n-tab-font-size);
 color: var(--n-tab-text-color);
 `,[o("addable",`
 padding-left: 8px;
 padding-right: 8px;
 font-size: 16px;
 `,[W("height-placeholder",`
 width: 0;
 font-size: var(--n-tab-font-size);
 `),St("disabled",[u("&:hover",`
 color: var(--n-tab-text-color-hover);
 `)])]),o("closable","padding-right: 8px;"),o("active",`
 background-color: #0000;
 font-weight: var(--n-tab-font-weight-active);
 color: var(--n-tab-text-color-active);
 `),o("disabled","color: var(--n-tab-text-color-disabled);")]),r("tabs-scroll-padding","border-bottom: 1px solid var(--n-tab-border-color);")]),o("left, right",[r("tabs-wrapper",`
 flex-direction: column;
 `,[r("tabs-tab-wrapper",`
 flex-direction: column;
 `,[r("tabs-tab-pad",`
 height: var(--n-tab-gap-vertical);
 width: 100%;
 `)])])]),o("top",[o("card-type",[r("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-top-right-radius: var(--n-tab-border-radius);
 `,[o("active",`
 border-bottom: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-bottom: 1px solid var(--n-tab-border-color);
 `)])]),o("left",[o("card-type",[r("tabs-tab",`
 border-top-left-radius: var(--n-tab-border-radius);
 border-bottom-left-radius: var(--n-tab-border-radius);
 `,[o("active",`
 border-right: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-right: 1px solid var(--n-tab-border-color);
 `)])]),o("right",[o("card-type",[r("tabs-tab",`
 border-top-right-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[o("active",`
 border-left: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-left: 1px solid var(--n-tab-border-color);
 `)])]),o("bottom",[o("card-type",[r("tabs-tab",`
 border-bottom-left-radius: var(--n-tab-border-radius);
 border-bottom-right-radius: var(--n-tab-border-radius);
 `,[o("active",`
 border-top: 1px solid #0000;
 `)]),r("tabs-tab-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `),r("tabs-pad",`
 border-top: 1px solid var(--n-tab-border-color);
 `)])])])]),Mt=Object.assign(Object.assign({},we.props),{value:[String,Number],defaultValue:[String,Number],trigger:{type:String,default:"click"},type:{type:String,default:"bar"},closable:Boolean,justifyContent:String,size:{type:String,default:"medium"},placement:{type:String,default:"top"},tabStyle:[String,Object],tabClass:String,addTabStyle:[String,Object],addTabClass:String,barWidth:Number,paneClass:String,paneStyle:[String,Object],paneWrapperClass:String,paneWrapperStyle:[String,Object],addable:[Boolean,Object],tabsPadding:{type:Number,default:0},animated:Boolean,onBeforeLeave:Function,onAdd:Function,"onUpdate:value":[Function,Array],onUpdateValue:[Function,Array],onClose:[Function,Array],labelSize:String,activeName:[String,Number],onActiveNameChange:[Function,Array]}),Ut=K({name:"Tabs",props:Mt,setup(e,{slots:i}){var c,v,d,y;const{mergedClsPrefixRef:h,inlineThemeDisabled:w}=Ct(e),S=we("Tabs","-tabs",Dt,jt,e,h),g=z(null),f=z(null),j=z(null),_=z(null),x=z(null),C=z(null),m=z(!0),$=z(!0),A=ve(e,["labelSize","size"]),T=ve(e,["activeName","value"]),D=z((v=(c=T.value)!==null&&c!==void 0?c:e.defaultValue)!==null&&v!==void 0?v:i.default?(y=(d=Z(i.default())[0])===null||d===void 0?void 0:d.props)===null||y===void 0?void 0:y.name:null),P=Rt(T,D),b={id:0},R=Y(()=>{if(!(!e.justifyContent||e.type==="card"))return{display:"flex",justifyContent:e.justifyContent}});ee(P,()=>{b.id=0,M(),le()});function k(){var t;const{value:a}=P;return a===null?null:(t=g.value)===null||t===void 0?void 0:t.querySelector(`[data-name="${a}"]`)}function Ce(t){if(e.type==="card")return;const{value:a}=f;if(!a)return;const n=a.style.opacity==="0";if(t){const s=`${h.value}-tabs-bar--disabled`,{barWidth:p,placement:L}=e;if(t.dataset.disabled==="true"?a.classList.add(s):a.classList.remove(s),["top","bottom"].includes(L)){if(se(["top","maxHeight","height"]),typeof p=="number"&&t.offsetWidth>=p){const O=Math.floor((t.offsetWidth-p)/2)+t.offsetLeft;a.style.left=`${O}px`,a.style.maxWidth=`${p}px`}else a.style.left=`${t.offsetLeft}px`,a.style.maxWidth=`${t.offsetWidth}px`;a.style.width="8192px",n&&(a.style.transition="none"),a.offsetWidth,n&&(a.style.transition="",a.style.opacity="1")}else{if(se(["left","maxWidth","width"]),typeof p=="number"&&t.offsetHeight>=p){const O=Math.floor((t.offsetHeight-p)/2)+t.offsetTop;a.style.top=`${O}px`,a.style.maxHeight=`${p}px`}else a.style.top=`${t.offsetTop}px`,a.style.maxHeight=`${t.offsetHeight}px`;a.style.height="8192px",n&&(a.style.transition="none"),a.offsetHeight,n&&(a.style.transition="",a.style.opacity="1")}}}function Re(){if(e.type==="card")return;const{value:t}=f;t&&(t.style.opacity="0")}function se(t){const{value:a}=f;if(a)for(const n of t)a.style[n]=""}function M(){if(e.type==="card")return;const t=k();t?Ce(t):Re()}function le(){var t;const a=(t=x.value)===null||t===void 0?void 0:t.$el;if(!a)return;const n=k();if(!n)return;const{scrollLeft:s,offsetWidth:p}=a,{offsetLeft:L,offsetWidth:O}=n;s>L?a.scrollTo({top:0,left:L,behavior:"smooth"}):L+O>s+p&&a.scrollTo({top:0,left:L+O-p,behavior:"smooth"})}const N=z(null);let q=0,H=null;function ze(t){const a=N.value;if(a){q=t.getBoundingClientRect().height;const n=`${q}px`,s=()=>{a.style.height=n,a.style.maxHeight=n};H?(s(),H(),H=null):H=s}}function Te(t){const a=N.value;if(a){const n=t.getBoundingClientRect().height,s=()=>{document.body.offsetHeight,a.style.maxHeight=`${n}px`,a.style.height=`${Math.max(q,n)}px`};H?(H(),H=null,s()):H=s}}function $e(){const t=N.value;if(t){t.style.maxHeight="",t.style.height="";const{paneWrapperStyle:a}=e;if(typeof a=="string")t.style.cssText=a;else if(a){const{maxHeight:n,height:s}=a;n!==void 0&&(t.style.maxHeight=n),s!==void 0&&(t.style.height=s)}}}const de={value:[]},ce=z("next");function Pe(t){const a=P.value;let n="next";for(const s of de.value){if(s===a)break;if(s===t){n="prev";break}}ce.value=n,We(t)}function We(t){const{onActiveNameChange:a,onUpdateValue:n,"onUpdate:value":s}=e;a&&U(a,t),n&&U(n,t),s&&U(s,t),D.value=t}function Le(t){const{onClose:a}=e;a&&U(a,t)}function be(){const{value:t}=f;if(!t)return;const a="transition-disabled";t.classList.add(a),M(),t.classList.remove(a)}const F=z(null);function J({transitionDisabled:t}){const a=g.value;if(!a)return;t&&a.classList.add("transition-disabled");const n=k();n&&F.value&&(F.value.style.width=`${n.offsetWidth}px`,F.value.style.height=`${n.offsetHeight}px`,F.value.style.transform=`translateX(${n.offsetLeft-Lt(getComputedStyle(a).paddingLeft)}px)`,t&&F.value.offsetWidth),t&&a.classList.remove("transition-disabled")}ee([P],()=>{e.type==="segment"&&ae(()=>{J({transitionDisabled:!1})})}),zt(()=>{e.type==="segment"&&J({transitionDisabled:!0})});let fe=0;function _e(t){var a;if(t.contentRect.width===0&&t.contentRect.height===0||fe===t.contentRect.width)return;fe=t.contentRect.width;const{type:n}=e;if((n==="line"||n==="bar")&&be(),n!=="segment"){const{placement:s}=e;Q((s==="top"||s==="bottom"?(a=x.value)===null||a===void 0?void 0:a.$el:C.value)||null)}}const Ae=re(_e,64);ee([()=>e.justifyContent,()=>e.size],()=>{ae(()=>{const{type:t}=e;(t==="line"||t==="bar")&&be()})});const V=z(!1);function Be(t){var a;const{target:n,contentRect:{width:s}}=t,p=n.parentElement.offsetWidth;if(!V.value)p<s&&(V.value=!0);else{const{value:L}=_;if(!L)return;p-s>L.$el.offsetWidth&&(V.value=!1)}Q(((a=x.value)===null||a===void 0?void 0:a.$el)||null)}const Ee=re(Be,64);function je(){const{onAdd:t}=e;t&&t(),ae(()=>{const a=k(),{value:n}=x;!a||!n||n.scrollTo({left:a.offsetLeft,top:0,behavior:"smooth"})})}function Q(t){if(!t)return;const{placement:a}=e;if(a==="top"||a==="bottom"){const{scrollLeft:n,scrollWidth:s,offsetWidth:p}=t;m.value=n<=0,$.value=n+p>=s}else{const{scrollTop:n,scrollHeight:s,offsetHeight:p}=t;m.value=n<=0,$.value=n+p>=s}}const ke=re(t=>{Q(t.target)},64);Tt(ie,{triggerRef:B(e,"trigger"),tabStyleRef:B(e,"tabStyle"),tabClassRef:B(e,"tabClass"),addTabStyleRef:B(e,"addTabStyle"),addTabClassRef:B(e,"addTabClass"),paneClassRef:B(e,"paneClass"),paneStyleRef:B(e,"paneStyle"),mergedClsPrefixRef:h,typeRef:B(e,"type"),closableRef:B(e,"closable"),valueRef:P,tabChangeIdRef:b,onBeforeLeaveRef:B(e,"onBeforeLeave"),activateTab:Pe,handleClose:Le,handleAdd:je}),$t(()=>{M(),le()}),Pt(()=>{const{value:t}=j;if(!t)return;const{value:a}=h,n=`${a}-tabs-nav-scroll-wrapper--shadow-start`,s=`${a}-tabs-nav-scroll-wrapper--shadow-end`;m.value?t.classList.remove(n):t.classList.add(n),$.value?t.classList.remove(s):t.classList.add(s)});const He={syncBarPosition:()=>{M()}},Oe=()=>{J({transitionDisabled:!0})},pe=Y(()=>{const{value:t}=A,{type:a}=e,n={card:"Card",bar:"Bar",line:"Line",segment:"Segment"}[a],s=`${t}${n}`,{self:{barColor:p,closeIconColor:L,closeIconColorHover:O,closeIconColorPressed:Fe,tabColor:Ie,tabBorderColor:De,paneTextColor:Me,tabFontWeight:Ne,tabBorderRadius:Ve,tabFontWeightActive:Xe,colorSegment:Ue,fontWeightStrong:Ge,tabColorSegment:Ye,closeSize:Ke,closeIconSize:qe,closeColorHover:Je,closeColorPressed:Qe,closeBorderRadius:Ze,[E("panePadding",t)]:X,[E("tabPadding",s)]:et,[E("tabPaddingVertical",s)]:tt,[E("tabGap",s)]:at,[E("tabGap",`${s}Vertical`)]:rt,[E("tabTextColor",a)]:nt,[E("tabTextColorActive",a)]:ot,[E("tabTextColorHover",a)]:it,[E("tabTextColorDisabled",a)]:st,[E("tabFontSize",t)]:lt},common:{cubicBezierEaseInOut:dt}}=S.value;return{"--n-bezier":dt,"--n-color-segment":Ue,"--n-bar-color":p,"--n-tab-font-size":lt,"--n-tab-text-color":nt,"--n-tab-text-color-active":ot,"--n-tab-text-color-disabled":st,"--n-tab-text-color-hover":it,"--n-pane-text-color":Me,"--n-tab-border-color":De,"--n-tab-border-radius":Ve,"--n-close-size":Ke,"--n-close-icon-size":qe,"--n-close-color-hover":Je,"--n-close-color-pressed":Qe,"--n-close-border-radius":Ze,"--n-close-icon-color":L,"--n-close-icon-color-hover":O,"--n-close-icon-color-pressed":Fe,"--n-tab-color":Ie,"--n-tab-font-weight":Ne,"--n-tab-font-weight-active":Xe,"--n-tab-padding":et,"--n-tab-padding-vertical":tt,"--n-tab-gap":at,"--n-tab-gap-vertical":rt,"--n-pane-padding-left":G(X,"left"),"--n-pane-padding-right":G(X,"right"),"--n-pane-padding-top":G(X,"top"),"--n-pane-padding-bottom":G(X,"bottom"),"--n-font-weight-strong":Ge,"--n-tab-color-segment":Ye}}),I=w?Wt("tabs",Y(()=>`${A.value[0]}${e.type[0]}`),pe,e):void 0;return Object.assign({mergedClsPrefix:h,mergedValue:P,renderedNames:new Set,segmentCapsuleElRef:F,tabsPaneWrapperRef:N,tabsElRef:g,barElRef:f,addTabInstRef:_,xScrollInstRef:x,scrollWrapperElRef:j,addTabFixed:V,tabWrapperStyle:R,handleNavResize:Ae,mergedSize:A,handleScroll:ke,handleTabsResize:Ee,cssVars:w?void 0:pe,themeClass:I==null?void 0:I.themeClass,animationDirection:ce,renderNameListRef:de,yScrollElRef:C,handleSegmentResize:Oe,onAnimationBeforeLeave:ze,onAnimationEnter:Te,onAnimationAfterEnter:$e,onRender:I==null?void 0:I.onRender},He)},render(){const{mergedClsPrefix:e,type:i,placement:c,addTabFixed:v,addable:d,mergedSize:y,renderNameListRef:h,onRender:w,paneWrapperClass:S,paneWrapperStyle:g,$slots:{default:f,prefix:j,suffix:_}}=this;w==null||w();const x=f?Z(f()).filter(b=>b.type.__TAB_PANE__===!0):[],C=f?Z(f()).filter(b=>b.type.__TAB__===!0):[],m=!C.length,$=i==="card",A=i==="segment",T=!$&&!A&&this.justifyContent;h.value=[];const D=()=>{const b=l("div",{style:this.tabWrapperStyle,class:[`${e}-tabs-wrapper`]},T?null:l("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}),m?x.map((R,k)=>(h.value.push(R.props.name),ne(l(oe,Object.assign({},R.props,{internalCreatedByPane:!0,internalLeftPadded:k!==0&&(!T||T==="center"||T==="start"||T==="end")}),R.children?{default:R.children.tab}:void 0)))):C.map((R,k)=>(h.value.push(R.props.name),ne(k!==0&&!T?me(R):R))),!v&&d&&$?xe(d,(m?x.length:C.length)!==0):null,T?null:l("div",{class:`${e}-tabs-scroll-padding`,style:{width:`${this.tabsPadding}px`}}));return l("div",{ref:"tabsElRef",class:`${e}-tabs-nav-scroll-content`},$&&d?l(te,{onResize:this.handleTabsResize},{default:()=>b}):b,$?l("div",{class:`${e}-tabs-pad`}):null,$?null:l("div",{ref:"barElRef",class:`${e}-tabs-bar`}))},P=A?"top":c;return l("div",{class:[`${e}-tabs`,this.themeClass,`${e}-tabs--${i}-type`,`${e}-tabs--${y}-size`,T&&`${e}-tabs--flex`,`${e}-tabs--${P}`],style:this.cssVars},l("div",{class:[`${e}-tabs-nav--${i}-type`,`${e}-tabs-nav--${P}`,`${e}-tabs-nav`]},he(j,b=>b&&l("div",{class:`${e}-tabs-nav__prefix`},b)),A?l(te,{onResize:this.handleSegmentResize},{default:()=>l("div",{class:`${e}-tabs-rail`,ref:"tabsElRef"},l("div",{class:`${e}-tabs-capsule`,ref:"segmentCapsuleElRef"},l("div",{class:`${e}-tabs-wrapper`},l("div",{class:`${e}-tabs-tab`}))),m?x.map((b,R)=>(h.value.push(b.props.name),l(oe,Object.assign({},b.props,{internalCreatedByPane:!0,internalLeftPadded:R!==0}),b.children?{default:b.children.tab}:void 0))):C.map((b,R)=>(h.value.push(b.props.name),R===0?b:me(b))))}):l(te,{onResize:this.handleNavResize},{default:()=>l("div",{class:`${e}-tabs-nav-scroll-wrapper`,ref:"scrollWrapperElRef"},["top","bottom"].includes(P)?l(Ft,{ref:"xScrollInstRef",onScroll:this.handleScroll},{default:D}):l("div",{class:`${e}-tabs-nav-y-scroll`,onScroll:this.handleScroll,ref:"yScrollElRef"},D()))}),v&&d&&$?xe(d,!0):null,he(_,b=>b&&l("div",{class:`${e}-tabs-nav__suffix`},b))),m&&(this.animated&&(P==="top"||P==="bottom")?l("div",{ref:"tabsPaneWrapperRef",style:g,class:[`${e}-tabs-pane-wrapper`,S]},ge(x,this.mergedValue,this.renderedNames,this.onAnimationBeforeLeave,this.onAnimationEnter,this.onAnimationAfterEnter,this.animationDirection)):ge(x,this.mergedValue,this.renderedNames)))}});function ge(e,i,c,v,d,y,h){const w=[];return e.forEach(S=>{const{name:g,displayDirective:f,"display-directive":j}=S.props,_=C=>f===C||j===C,x=i===g;if(S.key!==void 0&&(S.key=g),x||_("show")||_("show:lazy")&&c.has(g)){c.has(g)||c.add(g);const C=!_("if");w.push(C?_t(S,[[At,x]]):S)}}),h?l(Bt,{name:`${h}-transition`,onBeforeLeave:v,onEnter:d,onAfterEnter:y},{default:()=>w}):w}function xe(e,i){return l(oe,{ref:"addTabInstRef",key:"__addable",name:"__addable",internalCreatedByPane:!0,internalAddable:!0,internalLeftPadded:i,disabled:typeof e=="object"&&e.disabled})}function me(e){const i=Et(e);return i.props?i.props.internalLeftPadded=!0:i.props={internalLeftPadded:!0},i}function ne(e){return Array.isArray(e.dynamicProps)?e.dynamicProps.includes("internalLeftPadded")||e.dynamicProps.push("internalLeftPadded"):e.dynamicProps=["internalLeftPadded"],e}export{Xt as N,Ut as a};

import{A as W,cw as Be,q as $,m as T,o as oe,d as G,p as Q,cx as J,s as K,ct as Ee,I as ke,w as Ne,cf as _e,cy as Me,J as j,cz as Te,cA as Oe,cB as De,y as V,h as v,cC as Ie,T as ne,bL as q,c5 as ie,e as u,cD as X,f as E,c6 as O,a3 as F,g as Fe,x as He,u as se,cE as Ae,ca as Z,l as U,cF as ee,cG as Pe,v as je,z as Ge,L as Le,cg as I,cH as We,c4 as Ue,cI as Xe,c as Ye,by as Ve,cJ as A,cs as L,H as qe,i as Qe,cK as Je,G as Ke,cL as Ze,cM as te}from"./index-4af02034.js";import{g as et}from"./CrudTable-77c6359e.js";function tt(e){if(typeof e=="number")return{"":e.toString()};const t={};return e.split(/ +/).forEach(r=>{if(r==="")return;const[n,o]=r.split(":");o===void 0?t[""]=n:t[n]=o}),t}function H(e,t){var r;if(e==null)return;const n=tt(e);if(t===void 0)return n[""];if(typeof t=="string")return(r=n[t])!==null&&r!==void 0?r:n[""];if(Array.isArray(t)){for(let o=t.length-1;o>=0;--o){const a=t[o];if(a in n)return n[a]}return n[""]}else{let o,a=-1;return Object.keys(n).forEach(s=>{const l=Number(s);!Number.isNaN(l)&&t>=l&&l>=a&&(a=l,o=n[s])}),o}}function rt(e){var t;const r=(t=e.dirs)===null||t===void 0?void 0:t.find(({dir:n})=>n===W);return!!(r&&r.value===!1)}const ot={xs:0,s:640,m:1024,l:1280,xl:1536,"2xl":1920};function nt(e){return`(min-width: ${e}px)`}const P={};function it(e=ot){if(!Be)return $(()=>[]);if(typeof window.matchMedia!="function")return $(()=>[]);const t=T({}),r=Object.keys(e),n=(o,a)=>{o.matches?t.value[a]=!0:t.value[a]=!1};return r.forEach(o=>{const a=e[o];let s,l;P[a]===void 0?(s=window.matchMedia(nt(a)),s.addEventListener?s.addEventListener("change",f=>{l.forEach(h=>{h(f,o)})}):s.addListener&&s.addListener(f=>{l.forEach(h=>{h(f,o)})}),l=new Set,P[a]={mql:s,cbs:l}):(s=P[a].mql,l=P[a].cbs),l.add(n),s.matches&&l.forEach(f=>{f(s,o)})}),oe(()=>{r.forEach(o=>{const{cbs:a}=P[e[o]];a.has(n)&&a.delete(n)})}),$(()=>{const{value:o}=t;return r.filter(a=>o[a])})}const st=G({name:"NDrawerContent",inheritAttrs:!1,props:{blockScroll:Boolean,show:{type:Boolean,default:void 0},displayDirective:{type:String,required:!0},placement:{type:String,required:!0},contentClass:String,contentStyle:[Object,String],nativeScrollbar:{type:Boolean,required:!0},scrollbarProps:Object,trapFocus:{type:Boolean,default:!0},autoFocus:{type:Boolean,default:!0},showMask:{type:[Boolean,String],required:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,onClickoutside:Function,onAfterLeave:Function,onAfterEnter:Function,onEsc:Function},setup(e){const t=T(!!e.show),r=T(null),n=Q(J);let o=0,a="",s=null;const l=T(!1),f=T(!1),h=$(()=>e.placement==="top"||e.placement==="bottom"),{mergedClsPrefixRef:k,mergedRtlRef:z}=K(e),C=Ee("Drawer",z,k),R=i,w=d=>{f.value=!0,o=h.value?d.clientY:d.clientX,a=document.body.style.cursor,document.body.style.cursor=h.value?"ns-resize":"ew-resize",document.body.addEventListener("mousemove",g),document.body.addEventListener("mouseleave",R),document.body.addEventListener("mouseup",i)},y=()=>{s!==null&&(window.clearTimeout(s),s=null),f.value?l.value=!0:s=window.setTimeout(()=>{l.value=!0},300)},N=()=>{s!==null&&(window.clearTimeout(s),s=null),l.value=!1},{doUpdateHeight:p,doUpdateWidth:c}=n,_=d=>{const{maxWidth:b}=e;if(b&&d>b)return b;const{minWidth:x}=e;return x&&d<x?x:d},B=d=>{const{maxHeight:b}=e;if(b&&d>b)return b;const{minHeight:x}=e;return x&&d<x?x:d};function g(d){var b,x;if(f.value)if(h.value){let M=((b=r.value)===null||b===void 0?void 0:b.offsetHeight)||0;const D=o-d.clientY;M+=e.placement==="bottom"?D:-D,M=B(M),p(M),o=d.clientY}else{let M=((x=r.value)===null||x===void 0?void 0:x.offsetWidth)||0;const D=o-d.clientX;M+=e.placement==="right"?D:-D,M=_(M),c(M),o=d.clientX}}function i(){f.value&&(o=0,f.value=!1,document.body.style.cursor=a,document.body.removeEventListener("mousemove",g),document.body.removeEventListener("mouseup",i),document.body.removeEventListener("mouseleave",R))}ke(()=>{e.show&&(t.value=!0)}),Ne(()=>e.show,d=>{d||i()}),oe(()=>{i()});const m=$(()=>{const{show:d}=e,b=[[W,d]];return e.showMask||b.push([_e,e.onClickoutside,void 0,{capture:!0}]),b});function S(){var d;t.value=!1,(d=e.onAfterLeave)===null||d===void 0||d.call(e)}return Me($(()=>e.blockScroll&&t.value)),j(Te,r),j(Oe,null),j(De,null),{bodyRef:r,rtlEnabled:C,mergedClsPrefix:n.mergedClsPrefixRef,isMounted:n.isMountedRef,mergedTheme:n.mergedThemeRef,displayed:t,transitionName:$(()=>({right:"slide-in-from-right-transition",left:"slide-in-from-left-transition",top:"slide-in-from-top-transition",bottom:"slide-in-from-bottom-transition"})[e.placement]),handleAfterLeave:S,bodyDirectives:m,handleMousedownResizeTrigger:w,handleMouseenterResizeTrigger:y,handleMouseleaveResizeTrigger:N,isDragging:f,isHoverOnResizeTrigger:l}},render(){const{$slots:e,mergedClsPrefix:t}=this;return this.displayDirective==="show"||this.displayed||this.show?V(v("div",{role:"none"},v(Ie,{disabled:!this.showMask||!this.trapFocus,active:this.show,autoFocus:this.autoFocus,onEsc:this.onEsc},{default:()=>v(ne,{name:this.transitionName,appear:this.isMounted,onAfterEnter:this.onAfterEnter,onAfterLeave:this.handleAfterLeave},{default:()=>V(v("div",q(this.$attrs,{role:"dialog",ref:"bodyRef","aria-modal":"true",class:[`${t}-drawer`,this.rtlEnabled&&`${t}-drawer--rtl`,`${t}-drawer--${this.placement}-placement`,this.isDragging&&`${t}-drawer--unselectable`,this.nativeScrollbar&&`${t}-drawer--native-scrollbar`]}),[this.resizable?v("div",{class:[`${t}-drawer__resize-trigger`,(this.isDragging||this.isHoverOnResizeTrigger)&&`${t}-drawer__resize-trigger--hover`],onMouseenter:this.handleMouseenterResizeTrigger,onMouseleave:this.handleMouseleaveResizeTrigger,onMousedown:this.handleMousedownResizeTrigger}):null,this.nativeScrollbar?v("div",{class:[`${t}-drawer-content-wrapper`,this.contentClass],style:this.contentStyle,role:"none"},e):v(ie,Object.assign({},this.scrollbarProps,{contentStyle:this.contentStyle,contentClass:[`${t}-drawer-content-wrapper`,this.contentClass],theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar}),e)]),this.bodyDirectives)})})),[[W,this.displayDirective==="if"||this.displayed||this.show]]):null}}),{cubicBezierEaseIn:at,cubicBezierEaseOut:lt}=X;function dt({duration:e="0.3s",leaveDuration:t="0.2s",name:r="slide-in-from-right"}={}){return[u(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${at}`}),u(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${lt}`}),u(`&.${r}-transition-enter-to`,{transform:"translateX(0)"}),u(`&.${r}-transition-enter-from`,{transform:"translateX(100%)"}),u(`&.${r}-transition-leave-from`,{transform:"translateX(0)"}),u(`&.${r}-transition-leave-to`,{transform:"translateX(100%)"})]}const{cubicBezierEaseIn:ct,cubicBezierEaseOut:ut}=X;function ft({duration:e="0.3s",leaveDuration:t="0.2s",name:r="slide-in-from-left"}={}){return[u(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${ct}`}),u(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${ut}`}),u(`&.${r}-transition-enter-to`,{transform:"translateX(0)"}),u(`&.${r}-transition-enter-from`,{transform:"translateX(-100%)"}),u(`&.${r}-transition-leave-from`,{transform:"translateX(0)"}),u(`&.${r}-transition-leave-to`,{transform:"translateX(-100%)"})]}const{cubicBezierEaseIn:ht,cubicBezierEaseOut:vt}=X;function mt({duration:e="0.3s",leaveDuration:t="0.2s",name:r="slide-in-from-top"}={}){return[u(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${ht}`}),u(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${vt}`}),u(`&.${r}-transition-enter-to`,{transform:"translateY(0)"}),u(`&.${r}-transition-enter-from`,{transform:"translateY(-100%)"}),u(`&.${r}-transition-leave-from`,{transform:"translateY(0)"}),u(`&.${r}-transition-leave-to`,{transform:"translateY(-100%)"})]}const{cubicBezierEaseIn:bt,cubicBezierEaseOut:pt}=X;function gt({duration:e="0.3s",leaveDuration:t="0.2s",name:r="slide-in-from-bottom"}={}){return[u(`&.${r}-transition-leave-active`,{transition:`transform ${t} ${bt}`}),u(`&.${r}-transition-enter-active`,{transition:`transform ${e} ${pt}`}),u(`&.${r}-transition-enter-to`,{transform:"translateY(0)"}),u(`&.${r}-transition-enter-from`,{transform:"translateY(100%)"}),u(`&.${r}-transition-leave-from`,{transform:"translateY(0)"}),u(`&.${r}-transition-leave-to`,{transform:"translateY(100%)"})]}const wt=u([E("drawer",`
 word-break: break-word;
 line-height: var(--n-line-height);
 position: absolute;
 pointer-events: all;
 box-shadow: var(--n-box-shadow);
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 background-color: var(--n-color);
 color: var(--n-text-color);
 box-sizing: border-box;
 `,[dt(),ft(),mt(),gt(),O("unselectable",`
 user-select: none; 
 -webkit-user-select: none;
 `),O("native-scrollbar",[E("drawer-content-wrapper",`
 overflow: auto;
 height: 100%;
 `)]),F("resize-trigger",`
 position: absolute;
 background-color: #0000;
 transition: background-color .3s var(--n-bezier);
 `,[O("hover",`
 background-color: var(--n-resize-trigger-color-hover);
 `)]),E("drawer-content-wrapper",`
 box-sizing: border-box;
 `),E("drawer-content",`
 height: 100%;
 display: flex;
 flex-direction: column;
 `,[O("native-scrollbar",[E("drawer-body-content-wrapper",`
 height: 100%;
 overflow: auto;
 `)]),E("drawer-body",`
 flex: 1 0 0;
 overflow: hidden;
 `),E("drawer-body-content-wrapper",`
 box-sizing: border-box;
 padding: var(--n-body-padding);
 `),E("drawer-header",`
 font-weight: var(--n-title-font-weight);
 line-height: 1;
 font-size: var(--n-title-font-size);
 color: var(--n-title-text-color);
 padding: var(--n-header-padding);
 transition: border .3s var(--n-bezier);
 border-bottom: 1px solid var(--n-divider-color);
 border-bottom: var(--n-header-border-bottom);
 display: flex;
 justify-content: space-between;
 align-items: center;
 `,[F("close",`
 margin-left: 6px;
 transition:
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
 `)]),E("drawer-footer",`
 display: flex;
 justify-content: flex-end;
 border-top: var(--n-footer-border-top);
 transition: border .3s var(--n-bezier);
 padding: var(--n-footer-padding);
 `)]),O("right-placement",`
 top: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-bottom-left-radius: var(--n-border-radius);
 `,[F("resize-trigger",`
 width: 3px;
 height: 100%;
 top: 0;
 left: 0;
 transform: translateX(-1.5px);
 cursor: ew-resize;
 `)]),O("left-placement",`
 top: 0;
 bottom: 0;
 left: 0;
 border-top-right-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[F("resize-trigger",`
 width: 3px;
 height: 100%;
 top: 0;
 right: 0;
 transform: translateX(1.5px);
 cursor: ew-resize;
 `)]),O("top-placement",`
 top: 0;
 left: 0;
 right: 0;
 border-bottom-left-radius: var(--n-border-radius);
 border-bottom-right-radius: var(--n-border-radius);
 `,[F("resize-trigger",`
 width: 100%;
 height: 3px;
 bottom: 0;
 left: 0;
 transform: translateY(1.5px);
 cursor: ns-resize;
 `)]),O("bottom-placement",`
 left: 0;
 bottom: 0;
 right: 0;
 border-top-left-radius: var(--n-border-radius);
 border-top-right-radius: var(--n-border-radius);
 `,[F("resize-trigger",`
 width: 100%;
 height: 3px;
 top: 0;
 left: 0;
 transform: translateY(-1.5px);
 cursor: ns-resize;
 `)])]),u("body",[u(">",[E("drawer-container",`
 position: fixed;
 `)])]),E("drawer-container",`
 position: relative;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 `,[u("> *",`
 pointer-events: all;
 `)]),E("drawer-mask",`
 background-color: rgba(0, 0, 0, .3);
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 `,[O("invisible",`
 background-color: rgba(0, 0, 0, 0)
 `),Fe({enterDuration:"0.2s",leaveDuration:"0.2s",enterCubicBezier:"var(--n-bezier-in)",leaveCubicBezier:"var(--n-bezier-out)"})])]),yt=Object.assign(Object.assign({},se.props),{show:Boolean,width:[Number,String],height:[Number,String],placement:{type:String,default:"right"},maskClosable:{type:Boolean,default:!0},showMask:{type:[Boolean,String],default:!0},to:[String,Object],displayDirective:{type:String,default:"if"},nativeScrollbar:{type:Boolean,default:!0},zIndex:Number,onMaskClick:Function,scrollbarProps:Object,contentClass:String,contentStyle:[Object,String],trapFocus:{type:Boolean,default:!0},onEsc:Function,autoFocus:{type:Boolean,default:!0},closeOnEsc:{type:Boolean,default:!0},blockScroll:{type:Boolean,default:!0},maxWidth:Number,maxHeight:Number,minWidth:Number,minHeight:Number,resizable:Boolean,defaultWidth:{type:[Number,String],default:251},defaultHeight:{type:[Number,String],default:251},onUpdateWidth:[Function,Array],onUpdateHeight:[Function,Array],"onUpdate:width":[Function,Array],"onUpdate:height":[Function,Array],"onUpdate:show":[Function,Array],onUpdateShow:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,drawerStyle:[String,Object],drawerClass:String,target:null,onShow:Function,onHide:Function}),Bt=G({name:"Drawer",inheritAttrs:!1,props:yt,setup(e){const{mergedClsPrefixRef:t,namespaceRef:r,inlineThemeDisabled:n}=K(e),o=He(),a=se("Drawer","-drawer",wt,Ae,e,t),s=T(e.defaultWidth),l=T(e.defaultHeight),f=Z(U(e,"width"),s),h=Z(U(e,"height"),l),k=$(()=>{const{placement:i}=e;return i==="top"||i==="bottom"?"":ee(f.value)}),z=$(()=>{const{placement:i}=e;return i==="left"||i==="right"?"":ee(h.value)}),C=i=>{const{onUpdateWidth:m,"onUpdate:width":S}=e;m&&I(m,i),S&&I(S,i),s.value=i},R=i=>{const{onUpdateHeight:m,"onUpdate:width":S}=e;m&&I(m,i),S&&I(S,i),l.value=i},w=$(()=>[{width:k.value,height:z.value},e.drawerStyle||""]);function y(i){const{onMaskClick:m,maskClosable:S}=e;S&&_(!1),m&&m(i)}function N(i){y(i)}const p=Pe();function c(i){var m;(m=e.onEsc)===null||m===void 0||m.call(e),e.show&&e.closeOnEsc&&We(i)&&(p.value||_(!1))}function _(i){const{onHide:m,onUpdateShow:S,"onUpdate:show":d}=e;S&&I(S,i),d&&I(d,i),m&&!i&&I(m,i)}j(J,{isMountedRef:o,mergedThemeRef:a,mergedClsPrefixRef:t,doUpdateShow:_,doUpdateHeight:R,doUpdateWidth:C});const B=$(()=>{const{common:{cubicBezierEaseInOut:i,cubicBezierEaseIn:m,cubicBezierEaseOut:S},self:{color:d,textColor:b,boxShadow:x,lineHeight:M,headerPadding:D,footerPadding:ce,borderRadius:ue,bodyPadding:fe,titleFontSize:he,titleTextColor:ve,titleFontWeight:me,headerBorderBottom:be,footerBorderTop:pe,closeIconColor:ge,closeIconColorHover:we,closeIconColorPressed:ye,closeColorHover:Se,closeColorPressed:$e,closeIconSize:Ce,closeSize:Re,closeBorderRadius:xe,resizableTriggerColorHover:ze}}=a.value;return{"--n-line-height":M,"--n-color":d,"--n-border-radius":ue,"--n-text-color":b,"--n-box-shadow":x,"--n-bezier":i,"--n-bezier-out":S,"--n-bezier-in":m,"--n-header-padding":D,"--n-body-padding":fe,"--n-footer-padding":ce,"--n-title-text-color":ve,"--n-title-font-size":he,"--n-title-font-weight":me,"--n-header-border-bottom":be,"--n-footer-border-top":pe,"--n-close-icon-color":ge,"--n-close-icon-color-hover":we,"--n-close-icon-color-pressed":ye,"--n-close-size":Re,"--n-close-color-hover":Se,"--n-close-color-pressed":$e,"--n-close-icon-size":Ce,"--n-close-border-radius":xe,"--n-resize-trigger-color-hover":ze}}),g=n?je("drawer",void 0,B,e):void 0;return{mergedClsPrefix:t,namespace:r,mergedBodyStyle:w,handleOutsideClick:N,handleMaskClick:y,handleEsc:c,mergedTheme:a,cssVars:n?void 0:B,themeClass:g==null?void 0:g.themeClass,onRender:g==null?void 0:g.onRender,isMounted:o}},render(){const{mergedClsPrefix:e}=this;return v(Le,{to:this.to,show:this.show},{default:()=>{var t;return(t=this.onRender)===null||t===void 0||t.call(this),V(v("div",{class:[`${e}-drawer-container`,this.namespace,this.themeClass],style:this.cssVars,role:"none"},this.showMask?v(ne,{name:"fade-in-transition",appear:this.isMounted},{default:()=>this.show?v("div",{"aria-hidden":!0,class:[`${e}-drawer-mask`,this.showMask==="transparent"&&`${e}-drawer-mask--invisible`],onClick:this.handleMaskClick}):null}):null,v(st,Object.assign({},this.$attrs,{class:[this.drawerClass,this.$attrs.class],style:[this.mergedBodyStyle,this.$attrs.style],blockScroll:this.blockScroll,contentStyle:this.contentStyle,contentClass:this.contentClass,placement:this.placement,scrollbarProps:this.scrollbarProps,show:this.show,displayDirective:this.displayDirective,nativeScrollbar:this.nativeScrollbar,onAfterEnter:this.onAfterEnter,onAfterLeave:this.onAfterLeave,trapFocus:this.trapFocus,autoFocus:this.autoFocus,resizable:this.resizable,maxHeight:this.maxHeight,minHeight:this.minHeight,maxWidth:this.maxWidth,minWidth:this.minWidth,showMask:this.showMask,onEsc:this.handleEsc,onClickoutside:this.handleOutsideClick}),this.$slots)),[[Ge,{zIndex:this.zIndex,enabled:this.show}]])}})}}),St={title:String,headerClass:String,headerStyle:[Object,String],footerClass:String,footerStyle:[Object,String],bodyClass:String,bodyStyle:[Object,String],bodyContentClass:String,bodyContentStyle:[Object,String],nativeScrollbar:{type:Boolean,default:!0},scrollbarProps:Object,closable:Boolean},Et=G({name:"DrawerContent",props:St,setup(){const e=Q(J,null);e||Ue("drawer-content","`n-drawer-content` must be placed inside `n-drawer`.");const{doUpdateShow:t}=e;function r(){t(!1)}return{handleCloseClick:r,mergedTheme:e.mergedThemeRef,mergedClsPrefix:e.mergedClsPrefixRef}},render(){const{title:e,mergedClsPrefix:t,nativeScrollbar:r,mergedTheme:n,bodyClass:o,bodyStyle:a,bodyContentClass:s,bodyContentStyle:l,headerClass:f,headerStyle:h,footerClass:k,footerStyle:z,scrollbarProps:C,closable:R,$slots:w}=this;return v("div",{role:"none",class:[`${t}-drawer-content`,r&&`${t}-drawer-content--native-scrollbar`]},w.header||e||R?v("div",{class:[`${t}-drawer-header`,f],style:h,role:"none"},v("div",{class:`${t}-drawer-header__main`,role:"heading","aria-level":"1"},w.header!==void 0?w.header():e),R&&v(Xe,{onClick:this.handleCloseClick,clsPrefix:t,class:`${t}-drawer-header__close`,absolute:!0})):null,r?v("div",{class:[`${t}-drawer-body`,o],style:a,role:"none"},v("div",{class:[`${t}-drawer-body-content-wrapper`,s],style:l,role:"none"},w)):v(ie,Object.assign({themeOverrides:n.peerOverrides.Scrollbar,theme:n.peers.Scrollbar},C,{class:`${t}-drawer-body`,contentClass:[`${t}-drawer-body-content-wrapper`,s],contentStyle:l}),w),w.footer?v("div",{class:[`${t}-drawer-footer`,k],style:z,role:"none"},w.footer()):null)}}),re=1,ae=Ye("n-grid"),le=1,$t={span:{type:[Number,String],default:le},offset:{type:[Number,String],default:0},suffix:Boolean,privateOffset:Number,privateSpan:Number,privateColStart:Number,privateShow:{type:Boolean,default:!0}},kt=G({__GRID_ITEM__:!0,name:"GridItem",alias:["Gi"],props:$t,setup(){const{isSsrRef:e,xGapRef:t,itemStyleRef:r,overflowRef:n,layoutShiftDisabledRef:o}=Q(ae),a=Ve();return{overflow:n,itemStyle:r,layoutShiftDisabled:o,mergedXGap:$(()=>A(t.value||0)),deriveStyle:()=>{e.value;const{privateSpan:s=le,privateShow:l=!0,privateColStart:f=void 0,privateOffset:h=0}=a.vnode.props,{value:k}=t,z=A(k||0);return{display:l?"":"none",gridColumn:`${f!=null?f:`span ${s}`} / span ${s}`,marginLeft:h?`calc((100% - (${s} - 1) * ${z}) / ${s} * ${h} + ${z} * ${h})`:""}}}},render(){var e,t;if(this.layoutShiftDisabled){const{span:r,offset:n,mergedXGap:o}=this;return v("div",{style:{gridColumn:`span ${r} / span ${r}`,marginLeft:n?`calc((100% - (${r} - 1) * ${o}) / ${r} * ${n} + ${o} * ${n})`:""}},this.$slots)}return v("div",{style:[this.itemStyle,this.deriveStyle()]},(t=(e=this.$slots).default)===null||t===void 0?void 0:t.call(e,{overflow:this.overflow}))}}),Ct={xs:0,s:640,m:1024,l:1280,xl:1536,xxl:1920},de=24,Y="__ssr__",Rt={layoutShiftDisabled:Boolean,responsive:{type:[String,Boolean],default:"self"},cols:{type:[Number,String],default:de},itemResponsive:Boolean,collapsed:Boolean,collapsedRows:{type:Number,default:1},itemStyle:[Object,String],xGap:{type:[Number,String],default:0},yGap:{type:[Number,String],default:0}},Nt=G({name:"Grid",inheritAttrs:!1,props:Rt,setup(e){const{mergedClsPrefixRef:t,mergedBreakpointsRef:r}=K(e),n=/^\d+$/,o=T(void 0),a=it((r==null?void 0:r.value)||Ct),s=L(()=>!!(e.itemResponsive||!n.test(e.cols.toString())||!n.test(e.xGap.toString())||!n.test(e.yGap.toString()))),l=$(()=>{if(s.value)return e.responsive==="self"?o.value:a.value}),f=L(()=>{var p;return(p=Number(H(e.cols.toString(),l.value)))!==null&&p!==void 0?p:de}),h=L(()=>H(e.xGap.toString(),l.value)),k=L(()=>H(e.yGap.toString(),l.value)),z=p=>{o.value=p.contentRect.width},C=p=>{Ke(z,p)},R=T(!1),w=$(()=>{if(e.responsive==="self")return C}),y=T(!1),N=T();return qe(()=>{const{value:p}=N;p&&p.hasAttribute(Y)&&(p.removeAttribute(Y),y.value=!0)}),j(ae,{layoutShiftDisabledRef:U(e,"layoutShiftDisabled"),isSsrRef:y,itemStyleRef:U(e,"itemStyle"),xGapRef:h,overflowRef:R}),{isSsr:!Qe,contentEl:N,mergedClsPrefix:t,style:$(()=>e.layoutShiftDisabled?{width:"100%",display:"grid",gridTemplateColumns:`repeat(${e.cols}, minmax(0, 1fr))`,columnGap:A(e.xGap),rowGap:A(e.yGap)}:{width:"100%",display:"grid",gridTemplateColumns:`repeat(${f.value}, minmax(0, 1fr))`,columnGap:A(h.value),rowGap:A(k.value)}),isResponsive:s,responsiveQuery:l,responsiveCols:f,handleResize:w,overflow:R}},render(){if(this.layoutShiftDisabled)return v("div",q({ref:"contentEl",class:`${this.mergedClsPrefix}-grid`,style:this.style},this.$attrs),this.$slots);const e=()=>{var t,r,n,o,a,s,l;this.overflow=!1;const f=Ze(et(this)),h=[],{collapsed:k,collapsedRows:z,responsiveCols:C,responsiveQuery:R}=this;f.forEach(c=>{var _,B,g,i,m;if(((_=c==null?void 0:c.type)===null||_===void 0?void 0:_.__GRID_ITEM__)!==!0)return;if(rt(c)){const b=te(c);b.props?b.props.privateShow=!1:b.props={privateShow:!1},h.push({child:b,rawChildSpan:0});return}c.dirs=((B=c.dirs)===null||B===void 0?void 0:B.filter(({dir:b})=>b!==W))||null,((g=c.dirs)===null||g===void 0?void 0:g.length)===0&&(c.dirs=null);const S=te(c),d=Number((m=H((i=S.props)===null||i===void 0?void 0:i.span,R))!==null&&m!==void 0?m:re);d!==0&&h.push({child:S,rawChildSpan:d})});let w=0;const y=(t=h[h.length-1])===null||t===void 0?void 0:t.child;if(y!=null&&y.props){const c=(r=y.props)===null||r===void 0?void 0:r.suffix;c!==void 0&&c!==!1&&(w=Number((o=H((n=y.props)===null||n===void 0?void 0:n.span,R))!==null&&o!==void 0?o:re),y.props.privateSpan=w,y.props.privateColStart=C+1-w,y.props.privateShow=(a=y.props.privateShow)!==null&&a!==void 0?a:!0)}let N=0,p=!1;for(const{child:c,rawChildSpan:_}of h){if(p&&(this.overflow=!0),!p){const B=Number((l=H((s=c.props)===null||s===void 0?void 0:s.offset,R))!==null&&l!==void 0?l:0),g=Math.min(_+B,C);if(c.props?(c.props.privateSpan=g,c.props.privateOffset=B):c.props={privateSpan:g,privateOffset:B},k){const i=N%C;g+i>C&&(N+=C-i),g+N+w>z*C?p=!0:N+=g}}p&&(c.props?c.props.privateShow!==!0&&(c.props.privateShow=!1):c.props={privateShow:!1})}return v("div",q({ref:"contentEl",class:`${this.mergedClsPrefix}-grid`,style:this.style,[Y]:this.isSsr||void 0},this.$attrs),h.map(({child:c})=>c))};return this.isResponsive&&this.responsive==="self"?v(Je,{onResize:this.handleResize},{default:e}):e()}});export{Bt as N,Et as a,Nt as b,kt as c};

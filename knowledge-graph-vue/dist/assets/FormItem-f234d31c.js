import{p as Y,by as _e,w as me,o as Pe,f as $,c6 as S,e as N,c as ge,d as be,s as he,u as te,m as F,h as k,J as ae,dp as ve,di as le,q as h,cF as ne,bE as pe,cD as Ie,a3 as Z,l as ee,dq as oe,dr as Ce,H as Me,v as ze,T as Le,cv as Ae,ds as se,a9 as q,cn as de}from"./index-4af02034.js";function qe(t,e,l){var n;const c=Y(t,null);if(c===null)return;const o=(n=_e())===null||n===void 0?void 0:n.proxy;me(l,s),s(l.value),Pe(()=>{s(void 0,l.value)});function s(i,a){if(!c)return;const d=c[e];a!==void 0&&b(d,a),i!==void 0&&u(d,i)}function b(i,a){i[a]||(i[a]=[]),i[a].splice(i[a].findIndex(d=>d===o),1)}function u(i,a){i[a]||(i[a]=[]),~i[a].findIndex(d=>d===o)||i[a].push(o)}}const We=$("form",[S("inline",`
 width: 100%;
 display: inline-flex;
 align-items: flex-start;
 align-content: space-around;
 `,[$("form-item",{width:"auto",marginRight:"18px"},[N("&:last-child",{marginRight:0})])])]),K=ge("n-form"),ke=ge("n-form-item-insts");var je=globalThis&&globalThis.__awaiter||function(t,e,l,n){function c(o){return o instanceof l?o:new l(function(s){s(o)})}return new(l||(l=Promise))(function(o,s){function b(a){try{i(n.next(a))}catch(d){s(d)}}function u(a){try{i(n.throw(a))}catch(d){s(d)}}function i(a){a.done?o(a.value):c(a.value).then(b,u)}i((n=n.apply(t,e||[])).next())})};const Fe=Object.assign(Object.assign({},te.props),{inline:Boolean,labelWidth:[Number,String],labelAlign:String,labelPlacement:{type:String,default:"top"},model:{type:Object,default:()=>{}},rules:Object,disabled:Boolean,size:String,showRequireMark:{type:Boolean,default:void 0},requireMarkPlacement:String,showFeedback:{type:Boolean,default:!0},onSubmit:{type:Function,default:t=>{t.preventDefault()}},showLabel:{type:Boolean,default:void 0},validateMessages:Object}),De=be({name:"Form",props:Fe,setup(t){const{mergedClsPrefixRef:e}=he(t);te("Form","-form",We,ve,t,e);const l={},n=F(void 0),c=u=>{const i=n.value;(i===void 0||u>=i)&&(n.value=u)};function o(u){return je(this,arguments,void 0,function*(i,a=()=>!0){return yield new Promise((d,w)=>{const z=[];for(const r of le(l)){const I=l[r];for(const _ of I)_.path&&z.push(_.internalValidate(null,a))}Promise.all(z).then(r=>{const I=r.some(y=>!y.valid),_=[],W=[];r.forEach(y=>{var P,H;!((P=y.errors)===null||P===void 0)&&P.length&&_.push(y.errors),!((H=y.warnings)===null||H===void 0)&&H.length&&W.push(y.warnings)}),i&&i(_.length?_:void 0,{warnings:W.length?W:void 0}),I?w(_.length?_:void 0):d({warnings:W.length?W:void 0})})})})}function s(){for(const u of le(l)){const i=l[u];for(const a of i)a.restoreValidation()}}return ae(K,{props:t,maxChildLabelWidthRef:n,deriveMaxChildLabelWidth:c}),ae(ke,{formItems:l}),Object.assign({validate:o,restoreValidation:s},{mergedClsPrefix:e})},render(){const{mergedClsPrefix:t}=this;return k("form",{class:[`${t}-form`,this.inline&&`${t}-form--inline`],onSubmit:this.onSubmit},this.$slots)}});function Ve(t){const e=Y(K,null);return{mergedSize:h(()=>t.size!==void 0?t.size:(e==null?void 0:e.props.size)!==void 0?e.props.size:"medium")}}function Ee(t){const e=Y(K,null),l=h(()=>{const{labelPlacement:r}=t;return r!==void 0?r:e!=null&&e.props.labelPlacement?e.props.labelPlacement:"top"}),n=h(()=>l.value==="left"&&(t.labelWidth==="auto"||(e==null?void 0:e.props.labelWidth)==="auto")),c=h(()=>{if(l.value==="top")return;const{labelWidth:r}=t;if(r!==void 0&&r!=="auto")return ne(r);if(n.value){const I=e==null?void 0:e.maxChildLabelWidthRef.value;return I!==void 0?ne(I):void 0}if((e==null?void 0:e.props.labelWidth)!==void 0)return ne(e.props.labelWidth)}),o=h(()=>{const{labelAlign:r}=t;if(r)return r;if(e!=null&&e.props.labelAlign)return e.props.labelAlign}),s=h(()=>{var r;return[(r=t.labelProps)===null||r===void 0?void 0:r.style,t.labelStyle,{width:c.value}]}),b=h(()=>{const{showRequireMark:r}=t;return r!==void 0?r:e==null?void 0:e.props.showRequireMark}),u=h(()=>{const{requireMarkPlacement:r}=t;return r!==void 0?r:(e==null?void 0:e.props.requireMarkPlacement)||"right"}),i=F(!1),a=F(!1),d=h(()=>{const{validationStatus:r}=t;if(r!==void 0)return r;if(i.value)return"error";if(a.value)return"warning"}),w=h(()=>{const{showFeedback:r}=t;return r!==void 0?r:(e==null?void 0:e.props.showFeedback)!==void 0?e.props.showFeedback:!0}),z=h(()=>{const{showLabel:r}=t;return r!==void 0?r:(e==null?void 0:e.props.showLabel)!==void 0?e.props.showLabel:!0});return{validationErrored:i,validationWarned:a,mergedLabelStyle:s,mergedLabelPlacement:l,mergedLabelAlign:o,mergedShowRequireMark:b,mergedRequireMarkPlacement:u,mergedValidationStatus:d,mergedShowFeedback:w,mergedShowLabel:z,isAutoLabelWidth:n}}function Oe(t){const e=Y(K,null),l=h(()=>{const{rulePath:s}=t;if(s!==void 0)return s;const{path:b}=t;if(b!==void 0)return b}),n=h(()=>{const s=[],{rule:b}=t;if(b!==void 0&&(Array.isArray(b)?s.push(...b):s.push(b)),e){const{rules:u}=e.props,{value:i}=l;if(u!==void 0&&i!==void 0){const a=pe(u,i);a!==void 0&&(Array.isArray(a)?s.push(...a):s.push(a))}}return s}),c=h(()=>n.value.some(s=>s.required)),o=h(()=>c.value||t.required);return{mergedRules:n,mergedRequired:o}}const{cubicBezierEaseInOut:fe}=Ie;function Te({name:t="fade-down",fromOffset:e="-4px",enterDuration:l=".3s",leaveDuration:n=".3s",enterCubicBezier:c=fe,leaveCubicBezier:o=fe}={}){return[N(`&.${t}-transition-enter-from, &.${t}-transition-leave-to`,{opacity:0,transform:`translateY(${e})`}),N(`&.${t}-transition-enter-to, &.${t}-transition-leave-from`,{opacity:1,transform:"translateY(0)"}),N(`&.${t}-transition-leave-active`,{transition:`opacity ${n} ${o}, transform ${n} ${o}`}),N(`&.${t}-transition-enter-active`,{transition:`opacity ${l} ${c}, transform ${l} ${c}`})]}const Be=$("form-item",`
 display: grid;
 line-height: var(--n-line-height);
`,[$("form-item-label",`
 grid-area: label;
 align-items: center;
 line-height: 1.25;
 text-align: var(--n-label-text-align);
 font-size: var(--n-label-font-size);
 min-height: var(--n-label-height);
 padding: var(--n-label-padding);
 color: var(--n-label-text-color);
 transition: color .3s var(--n-bezier);
 box-sizing: border-box;
 font-weight: var(--n-label-font-weight);
 `,[Z("asterisk",`
 white-space: nowrap;
 user-select: none;
 -webkit-user-select: none;
 color: var(--n-asterisk-color);
 transition: color .3s var(--n-bezier);
 `),Z("asterisk-placeholder",`
 grid-area: mark;
 user-select: none;
 -webkit-user-select: none;
 visibility: hidden; 
 `)]),$("form-item-blank",`
 grid-area: blank;
 min-height: var(--n-blank-height);
 `),S("auto-label-width",[$("form-item-label","white-space: nowrap;")]),S("left-labelled",`
 grid-template-areas:
 "label blank"
 "label feedback";
 grid-template-columns: auto minmax(0, 1fr);
 grid-template-rows: auto 1fr;
 align-items: flex-start;
 `,[$("form-item-label",`
 display: grid;
 grid-template-columns: 1fr auto;
 min-height: var(--n-blank-height);
 height: auto;
 box-sizing: border-box;
 flex-shrink: 0;
 flex-grow: 0;
 `,[S("reverse-columns-space",`
 grid-template-columns: auto 1fr;
 `),S("left-mark",`
 grid-template-areas:
 "mark text"
 ". text";
 `),S("right-mark",`
 grid-template-areas: 
 "text mark"
 "text .";
 `),S("right-hanging-mark",`
 grid-template-areas: 
 "text mark"
 "text .";
 `),Z("text",`
 grid-area: text; 
 `),Z("asterisk",`
 grid-area: mark; 
 align-self: end;
 `)])]),S("top-labelled",`
 grid-template-areas:
 "label"
 "blank"
 "feedback";
 grid-template-rows: minmax(var(--n-label-height), auto) 1fr;
 grid-template-columns: minmax(0, 100%);
 `,[S("no-label",`
 grid-template-areas:
 "blank"
 "feedback";
 grid-template-rows: 1fr;
 `),$("form-item-label",`
 display: flex;
 align-items: flex-start;
 justify-content: var(--n-label-text-align);
 `)]),$("form-item-blank",`
 box-sizing: border-box;
 display: flex;
 align-items: center;
 position: relative;
 `),$("form-item-feedback-wrapper",`
 grid-area: feedback;
 box-sizing: border-box;
 min-height: var(--n-feedback-height);
 font-size: var(--n-feedback-font-size);
 line-height: 1.25;
 transform-origin: top left;
 `,[N("&:not(:empty)",`
 padding: var(--n-feedback-padding);
 `),$("form-item-feedback",{transition:"color .3s var(--n-bezier)",color:"var(--n-feedback-text-color)"},[S("warning",{color:"var(--n-feedback-text-color-warning)"}),S("error",{color:"var(--n-feedback-text-color-error)"}),Te({fromOffset:"-3px",enterDuration:".3s",leaveDuration:".2s"})])])]);var ce=globalThis&&globalThis.__awaiter||function(t,e,l,n){function c(o){return o instanceof l?o:new l(function(s){s(o)})}return new(l||(l=Promise))(function(o,s){function b(a){try{i(n.next(a))}catch(d){s(d)}}function u(a){try{i(n.throw(a))}catch(d){s(d)}}function i(a){a.done?o(a.value):c(a.value).then(b,u)}i((n=n.apply(t,e||[])).next())})};const Ne=Object.assign(Object.assign({},te.props),{label:String,labelWidth:[Number,String],labelStyle:[String,Object],labelAlign:String,labelPlacement:String,path:String,first:Boolean,rulePath:String,required:Boolean,showRequireMark:{type:Boolean,default:void 0},requireMarkPlacement:String,showFeedback:{type:Boolean,default:void 0},rule:[Object,Array],size:String,ignorePathChange:Boolean,validationStatus:String,feedback:String,feedbackClass:String,feedbackStyle:[String,Object],showLabel:{type:Boolean,default:void 0},labelProps:Object});function ue(t,e){return(...l)=>{try{const n=t(...l);return!e&&(typeof n=="boolean"||n instanceof Error||Array.isArray(n))||n!=null&&n.then?n:(n===void 0||de("form-item/validate",`You return a ${typeof n} typed value in the validator method, which is not recommended. Please use ${e?"`Promise`":"`boolean`, `Error` or `Promise`"} typed value instead.`),!0)}catch(n){de("form-item/validate","An error is catched in the validation, so the validation won't be done. Your callback in `validate` method of `n-form` or `n-form-item` won't be called in this validation."),console.error(n);return}}}const Ye=be({name:"FormItem",props:Ne,setup(t){qe(ke,"formItems",ee(t,"path"));const{mergedClsPrefixRef:e,inlineThemeDisabled:l}=he(t),n=Y(K,null),c=Ve(t),o=Ee(t),{validationErrored:s,validationWarned:b}=o,{mergedRequired:u,mergedRules:i}=Oe(t),{mergedSize:a}=c,{mergedLabelPlacement:d,mergedLabelAlign:w,mergedRequireMarkPlacement:z}=o,r=F([]),I=F(oe()),_=n?ee(n.props,"disabled"):F(!1),W=te("Form","-form-item",Be,ve,t,e);me(ee(t,"path"),()=>{t.ignorePathChange||y()});function y(){r.value=[],s.value=!1,b.value=!1,t.feedback&&(I.value=oe())}const P=(...m)=>ce(this,[...m],void 0,function*(R=null,C=()=>!0,v={suppressWarning:!0}){const{path:M}=t;v?v.first||(v.first=t.first):v={};const{value:j}=i,E=n?pe(n.props.model,M||""):void 0,O={},T={},L=(R?j.filter(f=>Array.isArray(f.trigger)?f.trigger.includes(R):f.trigger===R):j).filter(C).map((f,p)=>{const g=Object.assign({},f);if(g.validator&&(g.validator=ue(g.validator,!1)),g.asyncValidator&&(g.asyncValidator=ue(g.asyncValidator,!0)),g.renderMessage){const X=`__renderMessage__${p}`;T[X]=g.message,g.message=X,O[X]=g.renderMessage}return g}),A=L.filter(f=>f.level!=="warning"),J=L.filter(f=>f.level==="warning"),x={valid:!0,errors:void 0,warnings:void 0};if(!L.length)return x;const B=M!=null?M:"__n_no_path__",U=new se({[B]:A}),G=new se({[B]:J}),{validateMessages:D}=(n==null?void 0:n.props)||{};D&&(U.messages(D),G.messages(D));const Q=f=>{r.value=f.map(p=>{const g=(p==null?void 0:p.message)||"";return{key:g,render:()=>g.startsWith("__renderMessage__")?O[g]():g}}),f.forEach(p=>{var g;!((g=p.message)===null||g===void 0)&&g.startsWith("__renderMessage__")&&(p.message=T[p.message])})};if(A.length){const f=yield new Promise(p=>{U.validate({[B]:E},v,p)});f!=null&&f.length&&(x.valid=!1,x.errors=f,Q(f))}if(J.length&&!x.errors){const f=yield new Promise(p=>{G.validate({[B]:E},v,p)});f!=null&&f.length&&(Q(f),x.warnings=f)}return!x.errors&&!x.warnings?y():(s.value=!!x.errors,b.value=!!x.warnings),x});function H(){P("blur")}function we(){P("change")}function Re(){P("focus")}function xe(){P("input")}function ye(m,R){return ce(this,void 0,void 0,function*(){let C,v,M,j;return typeof m=="string"?(C=m,v=R):m!==null&&typeof m=="object"&&(C=m.trigger,v=m.callback,M=m.shouldRuleBeApplied,j=m.options),yield new Promise((E,O)=>{P(C,M,j).then(({valid:T,errors:L,warnings:A})=>{T?(v&&v(void 0,{warnings:A}),E({warnings:A})):(v&&v(L,{warnings:A}),O(L))})})})}ae(Ce,{path:ee(t,"path"),disabled:_,mergedSize:c.mergedSize,mergedValidationStatus:o.mergedValidationStatus,restoreValidation:y,handleContentBlur:H,handleContentChange:we,handleContentFocus:Re,handleContentInput:xe});const Se={validate:ye,restoreValidation:y,internalValidate:P},ie=F(null);Me(()=>{if(!o.isAutoLabelWidth.value)return;const m=ie.value;if(m!==null){const R=m.style.whiteSpace;m.style.whiteSpace="nowrap",m.style.width="",n==null||n.deriveMaxChildLabelWidth(Number(getComputedStyle(m).width.slice(0,-2))),m.style.whiteSpace=R}});const re=h(()=>{var m;const{value:R}=a,{value:C}=d,v=C==="top"?"vertical":"horizontal",{common:{cubicBezierEaseInOut:M},self:{labelTextColor:j,asteriskColor:E,lineHeight:O,feedbackTextColor:T,feedbackTextColorWarning:L,feedbackTextColorError:A,feedbackPadding:J,labelFontWeight:x,[q("labelHeight",R)]:B,[q("blankHeight",R)]:U,[q("feedbackFontSize",R)]:G,[q("feedbackHeight",R)]:D,[q("labelPadding",v)]:Q,[q("labelTextAlign",v)]:f,[q(q("labelFontSize",C),R)]:p}}=W.value;let g=(m=w.value)!==null&&m!==void 0?m:f;return C==="top"&&(g=g==="right"?"flex-end":"flex-start"),{"--n-bezier":M,"--n-line-height":O,"--n-blank-height":U,"--n-label-font-size":p,"--n-label-text-align":g,"--n-label-height":B,"--n-label-padding":Q,"--n-label-font-weight":x,"--n-asterisk-color":E,"--n-label-text-color":j,"--n-feedback-padding":J,"--n-feedback-font-size":G,"--n-feedback-height":D,"--n-feedback-text-color":T,"--n-feedback-text-color-warning":L,"--n-feedback-text-color-error":A}}),V=l?ze("form-item",h(()=>{var m;return`${a.value[0]}${d.value[0]}${((m=w.value)===null||m===void 0?void 0:m[0])||""}`}),re,t):void 0,$e=h(()=>d.value==="left"&&z.value==="left"&&w.value==="left");return Object.assign(Object.assign(Object.assign(Object.assign({labelElementRef:ie,mergedClsPrefix:e,mergedRequired:u,feedbackId:I,renderExplains:r,reverseColSpace:$e},o),c),Se),{cssVars:l?void 0:re,themeClass:V==null?void 0:V.themeClass,onRender:V==null?void 0:V.onRender})},render(){const{$slots:t,mergedClsPrefix:e,mergedShowLabel:l,mergedShowRequireMark:n,mergedRequireMarkPlacement:c,onRender:o}=this,s=n!==void 0?n:this.mergedRequired;o==null||o();const b=()=>{const u=this.$slots.label?this.$slots.label():this.label;if(!u)return null;const i=k("span",{class:`${e}-form-item-label__text`},u),a=s?k("span",{class:`${e}-form-item-label__asterisk`},c!=="left"?" *":"* "):c==="right-hanging"&&k("span",{class:`${e}-form-item-label__asterisk-placeholder`}," *"),{labelProps:d}=this;return k("label",Object.assign({},d,{class:[d==null?void 0:d.class,`${e}-form-item-label`,`${e}-form-item-label--${c}-mark`,this.reverseColSpace&&`${e}-form-item-label--reverse-columns-space`],style:this.mergedLabelStyle,ref:"labelElementRef"}),c==="left"?[a,i]:[i,a])};return k("div",{class:[`${e}-form-item`,this.themeClass,`${e}-form-item--${this.mergedSize}-size`,`${e}-form-item--${this.mergedLabelPlacement}-labelled`,this.isAutoLabelWidth&&`${e}-form-item--auto-label-width`,!l&&`${e}-form-item--no-label`],style:this.cssVars},l&&b(),k("div",{class:[`${e}-form-item-blank`,this.mergedValidationStatus&&`${e}-form-item-blank--${this.mergedValidationStatus}`]},t),this.mergedShowFeedback?k("div",{key:this.feedbackId,style:this.feedbackStyle,class:[`${e}-form-item-feedback-wrapper`,this.feedbackClass]},k(Le,{name:"fade-down-transition",mode:"out-in"},{default:()=>{const{mergedValidationStatus:u}=this;return Ae(t.feedback,i=>{var a;const{feedback:d}=this,w=i||d?k("div",{key:"__feedback__",class:`${e}-form-item-feedback__line`},i||d):this.renderExplains.length?(a=this.renderExplains)===null||a===void 0?void 0:a.map(({key:z,render:r})=>k("div",{key:z,class:`${e}-form-item-feedback__line`},r())):null;return w?u==="warning"?k("div",{key:"controlled-warning",class:`${e}-form-item-feedback ${e}-form-item-feedback--warning`},w):u==="error"?k("div",{key:"controlled-error",class:`${e}-form-item-feedback ${e}-form-item-feedback--error`},w):u==="success"?k("div",{key:"controlled-success",class:`${e}-form-item-feedback ${e}-form-item-feedback--success`},w):k("div",{key:"controlled-default",class:`${e}-form-item-feedback`},w):null})}})):null)}});export{De as N,Ye as a};

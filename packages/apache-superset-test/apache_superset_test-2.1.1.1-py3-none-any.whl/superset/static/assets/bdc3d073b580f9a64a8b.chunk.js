"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4194],{44194:(e,t,a)=>{a.r(t),a.d(t,{default:()=>J}),a(67294);var i=a(43323),s=a(51995),o=a(45697),r=a.n(o),n=a(23493),l=a.n(n),c=a(21804),h=a.n(c),m=a(15078),y=a.n(m),u=a(30381),d=a.n(u),p=a(28041),x=a.n(p),g=a(28062),b=a(67190),f=a(61988),k=a(45636),v=a(51115),A=a(40962),w=a(37731),L=a(60524),M=a(95963),C=a(83937),$=a(80221);const T=r().oneOfType([r().number,r().oneOf(["auto"])]),F=r().oneOfType([r().string,r().shape({label:r().string})]),_=r().shape({r:r().number.isRequired,g:r().number.isRequired,b:r().number.isRequired}),D=r().shape({x:r().number,y:r().number}),O=r().shape({x:r().string,y:r().number}),S=r().shape({outliers:r().arrayOf(r().number),Q1:r().number,Q2:r().number,Q3:r().number,whisker_high:r().number,whisker_low:r().number}),E=r().shape({markerLabels:r().arrayOf(r().string),markerLineLabels:r().arrayOf(r().string),markerLines:r().arrayOf(r().number),markers:r().arrayOf(r().number),measures:r().arrayOf(r().number),rangeLabels:r().arrayOf(r().string),ranges:r().arrayOf(r().number)}),N=r().shape({annotationType:r().oneOf(Object.keys(M.DT)),color:r().string,hideLine:r().bool,name:r().string,opacity:r().string,show:r().bool,showMarkers:r().bool,sourceType:r().string,style:r().string,value:r().oneOfType([r().number,r().string]),width:r().number}),B=[{text:"No data",dy:"-.75em",class:"header"},{text:"Adjust filters or check the Datasource.",dy:".75em",class:"body"}];x().utils.noData=function(e,t){const a=e.options().margin(),i=x().utils.availableHeight(null,t,a),s=x().utils.availableWidth(null,t,a),o=a.left+s/2,r=a.top+i/2;t.selectAll("g").remove();const n=t.selectAll(".nv-noData").data(B);n.enter().append("text").attr("class",(e=>`nvd3 nv-noData ${e.class}`)).attr("dy",(e=>e.dy)).style("text-anchor","middle"),n.attr("x",o).attr("y",r).text((e=>e.text))};const{getColor:z,getScale:G}=g,I=["line","dual_line","line_multi","area","compare","bar","time_pivot"],R={data:r().oneOfType([r().arrayOf(r().oneOfType([O,r().shape({key:r().string,values:r().arrayOf(O)}),r().shape({key:r().arrayOf(r().string),values:r().arrayOf(D)}),r().shape({classed:r().string,key:r().string,type:r().string,values:r().arrayOf(D),yAxis:r().number}),r().shape({label:r().string,values:r().arrayOf(S)}),r().shape({key:r().string,values:r().arrayOf(r().object)})])),E]),width:r().number,height:r().number,annotationData:r().object,annotationLayers:r().arrayOf(N),bottomMargin:T,colorScheme:r().string,comparisonType:r().string,contribution:r().bool,leftMargin:T,onError:r().func,showLegend:r().bool,showMarkers:r().bool,useRichTooltip:r().bool,vizType:r().oneOf(["area","bar","box_plot","bubble","bullet","compare","column","dist_bar","line","line_multi","time_pivot","pie","dual_line"]),xAxisFormat:r().string,numberFormat:r().string,xAxisLabel:r().string,xAxisShowMinMax:r().bool,xIsLogScale:r().bool,xTicksLayout:r().oneOf(["auto","staggered","45°"]),yAxisFormat:r().string,yAxisBounds:r().arrayOf(r().number),yAxisLabel:r().string,yAxisShowMinMax:r().bool,yIsLogScale:r().bool,orderBars:r().bool,isBarStacked:r().bool,showBarValue:r().bool,reduceXTicks:r().bool,showControls:r().bool,showBrush:r().oneOf([!0,"yes",!1,"no","auto"]),onBrushEnd:r().func,yAxis2Format:r().string,lineInterpolation:r().string,isDonut:r().bool,isPieLabelOutside:r().bool,pieLabelType:r().oneOf(["key","value","percent","key_value","key_percent","key_value_percent"]),showLabels:r().bool,areaStackedStyle:r().string,entity:r().string,maxBubbleSize:r().number,xField:F,yField:F,sizeField:F,baseColor:_},Z=()=>{},P=(0,b.JB)();function V(e,t){const{data:a,width:i,height:s,annotationData:o,annotationLayers:r=[],areaStackedStyle:n,baseColor:c,bottomMargin:m,colorScheme:u,comparisonType:p,contribution:g,entity:T,isBarStacked:F,isDonut:_,isPieLabelOutside:D,leftMargin:O,lineInterpolation:S="linear",markerLabels:E,markerLines:N,markerLineLabels:B,markers:R,maxBubbleSize:V,onBrushEnd:H=Z,onError:U=Z,orderBars:W,pieLabelType:q,rangeLabels:J,ranges:j,reduceXTicks:X=!1,showBarValue:Q,showBrush:Y,showControls:K,showLabels:ee,showLegend:te,showMarkers:ae,sizeField:ie,useRichTooltip:se,vizType:oe,xAxisFormat:re,numberFormat:ne,xAxisLabel:le,xAxisShowMinMax:ce=!1,xField:he,xIsLogScale:me,xTicksLayout:ye,yAxisFormat:ue,yAxis2Format:de,yAxisBounds:pe,yAxis2Bounds:xe,yAxisLabel:ge,yAxisShowMinMax:be=!1,yAxis2ShowMinMax:fe=!1,yField:ke,yIsLogScale:ve,sliceId:Ae}=t,we=null!==document.querySelector("#explorer-container"),Le=e;Le.innerHTML="";const Me=r.filter((e=>e.show));let Ce,$e=Le,Te=null;for(;$e.parentElement;){if($e.parentElement.id.startsWith("chart-id-")){Te=$e.parentElement.id;break}$e=$e.parentElement}let Fe=i,_e="key";function De(e){return e.includes(oe)}Le.style.width=`${i}px`,Le.style.height=`${s}px`,Te?(0,$.o2)(Te):(0,$.Vl)(!0),x().addGraph((function(){const t=y().select(e);t.classed("superset-legacy-chart-nvd3",!0),t.classed(`superset-legacy-chart-nvd3-${h()(oe)}`,!0);let r=t.select("svg");r.empty()&&(r=t.append("svg"));const Le="bullet"===oe?Math.min(s,50):s,$e=De(I),Oe="staggered"===ye,Se="auto"===ye&&De(["column","dist_bar"])||"45°"===ye?45:0;if(45===Se&&(0,C.Z)(Y))return U((0,f.t)("You cannot use 45° tick layout along with the time range filter")),null;const Ee=(0,C.Z)(Y)||"auto"===Y&&s>=480&&"45°"!==ye,Ne=(0,b.JB)(ne);switch(oe){case"line":Ee?(Ce=x().models.lineWithFocusChart(),Oe&&(Ce.focus.margin({bottom:40}),Ce.focusHeight(80)),Ce.focus.xScale(y().time.scale.utc())):Ce=x().models.lineChart(),Ce.xScale(y().time.scale.utc()),Ce.interpolate(S),Ce.clipEdge(!1);break;case"time_pivot":Ce=x().models.lineChart(),Ce.xScale(y().time.scale.utc()),Ce.interpolate(S);break;case"dual_line":case"line_multi":Ce=x().models.multiChart(),Ce.interpolate(S),Ce.xScale(y().time.scale.utc());break;case"bar":Ce=x().models.multiBarChart().showControls(K).groupSpacing(.1),X||(Fe=(0,$.UG)(a,F,i)),Ce.width(Fe),Ce.xAxis.showMaxMin(!1),Ce.stacked(F);break;case"dist_bar":Ce=x().models.multiBarChart().showControls(K).reduceXTicks(X).groupSpacing(.1),Ce.xAxis.showMaxMin(!1),Ce.stacked(F),W&&a.forEach((e=>{const t=[...e.values];e.values=t.sort(((e,t)=>(0,$.Hy)(e.x)<(0,$.Hy)(t.x)?-1:1))})),X||(Fe=(0,$.UG)(a,F,i)),Ce.width(Fe);break;case"pie":if(Ce=x().models.pieChart(),_e="x",Ce.valueFormat(Ne),_&&Ce.donut(!0),Ce.showLabels(ee),Ce.labelsOutside(D),Ce.labelThreshold(.05),Ce.cornerRadius(!0),["key","value","percent"].includes(q))Ce.labelType(q);else if("key_value"===q)Ce.labelType((e=>`${e.data.x}: ${Ne(e.data.y)}`));else{const e=y().sum(a,(e=>e.y)),t=(0,b.JB)(k.Z.PERCENT_2_POINT);"key_percent"===q?(Ce.tooltip.valueFormatter((e=>t(e))),Ce.labelType((a=>`${a.data.x}: ${t(a.data.y/e)}`))):(Ce.tooltip.valueFormatter((a=>`${Ne(a)} (${t(a/e)})`)),Ce.labelType((a=>`${a.data.x}: ${Ne(a.data.y)} (${t(a.data.y/e)})`)))}Ce.margin({top:0});break;case"column":Ce=x().models.multiBarChart().reduceXTicks(!1);break;case"compare":Ce=x().models.cumulativeLineChart(),Ce.xScale(y().time.scale.utc()),Ce.useInteractiveGuideline(!0),Ce.xAxis.showMaxMin(!1);break;case"bubble":Ce=x().models.scatterChart(),Ce.showDistX(!1),Ce.showDistY(!1),Ce.tooltip.contentGenerator((e=>(0,$.zK)({point:e.point,entity:T,xField:he,yField:ke,sizeField:ie,xFormatter:(0,$.fF)(re),yFormatter:(0,$.fF)(ue),sizeFormatter:P}))),Ce.pointRange([5,V**2]),Ce.pointDomain([0,y().max(a,(e=>y().max(e.values,(e=>e.size))))]);break;case"area":Ce=x().models.stackedAreaChart(),Ce.showControls(K),Ce.style(n),Ce.xScale(y().time.scale.utc());break;case"box_plot":_e="label",Ce=x().models.boxPlotChart(),Ce.x((e=>e.label)),Ce.maxBoxWidth(75);break;case"bullet":Ce=x().models.bulletChart(),a.rangeLabels=J,a.ranges=j,a.markerLabels=E,a.markerLines=N,a.markerLineLabels=B,a.markers=R;break;default:throw new Error(`Unrecognized visualization for nvd3${oe}`)}let Be;Ce.margin({left:0,bottom:0}),Q&&((0,$.Ad)(r,a,F,ue),Ce.dispatch.on("stateChange.drawBarValues",(()=>{(0,$.Ad)(r,a,F,ue)}))),Ee&&H!==Z&&Ce.focus&&Ce.focus.dispatch.on("brush",(e=>{const t=(0,$.z_)(e.extent);t&&e.brush.on("brushend",(()=>{H(t)}))})),Ce.xAxis&&Ce.xAxis.staggerLabels&&Ce.xAxis.staggerLabels(Oe),Ce.xAxis&&Ce.xAxis.rotateLabels&&Ce.xAxis.rotateLabels(Se),Ce.x2Axis&&Ce.x2Axis.staggerLabels&&Ce.x2Axis.staggerLabels(Oe),Ce.x2Axis&&Ce.x2Axis.rotateLabels&&Ce.x2Axis.rotateLabels(Se),"showLegend"in Ce&&void 0!==te&&(Fe<340&&"pie"!==oe?Ce.showLegend(!1):Ce.showLegend(te)),ve&&Ce.yScale(y().scale.log()),me&&Ce.xScale(y().scale.log()),$e?(Be=(0,v.bt)(re),Ce.interactiveLayer.tooltip.headerFormatter(A.Z)):Be=(0,$.fF)(re),Ce.x2Axis&&Ce.x2Axis.tickFormat&&Ce.x2Axis.tickFormat(Be),Ce.xAxis&&Ce.xAxis.tickFormat&&(De(["dist_bar","box_plot"])?Ce.xAxis.tickFormat((e=>e.length>40?`${e.slice(0,Math.max(0,40))}…`:e)):Ce.xAxis.tickFormat(Be));let ze=(0,$.fF)(ue);if(Ce.yAxis&&Ce.yAxis.tickFormat&&(!g&&"percentage"!==p||ue&&ue!==k.Z.SMART_NUMBER&&ue!==k.Z.SMART_NUMBER_SIGNED||(ze=(0,b.JB)(k.Z.PERCENT_1_POINT)),Ce.yAxis.tickFormat(ze)),Ce.y2Axis&&Ce.y2Axis.tickFormat&&Ce.y2Axis.tickFormat(ze),Ce.yAxis&&Ce.yAxis.ticks(5),Ce.y2Axis&&Ce.y2Axis.ticks(5),(0,$.Ml)(Ce.xAxis,ce),(0,$.Ml)(Ce.x2Axis,ce),(0,$.Ml)(Ce.yAxis,be),(0,$.Ml)(Ce.y2Axis,fe||be),"time_pivot"===oe){if(c){const{r:e,g:t,b:a}=c;Ce.color((i=>{const s=i.rank>0?.5*i.perc:1;return`rgba(${e}, ${t}, ${a}, ${s})`}))}Ce.useInteractiveGuideline(!0),Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.RO)(e,Be,ze)))}else if("bullet"!==oe){const e=G(u);Ce.color((t=>t.color||e((0,$.gO)(t[_e]),Ae)))}if(De(["line","area","bar","dist_bar"])&&se&&(Ce.useInteractiveGuideline(!0),"line"===oe||"bar"===oe?Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.Gx)(e,A.Z,ze))):"dist_bar"===oe?Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.yy)(e,ze))):Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.n4)(e,A.Z,ze,Ce)))),De(["compare"])&&Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.yy)(e,ze))),De(["dual_line","line_multi"])){const e=(0,b.JB)(ue),t=(0,b.JB)(de);Ce.yAxis1.tickFormat(e),Ce.yAxis2.tickFormat(t);const i=a.map((a=>1===a.yAxis?e:t));Ce.useInteractiveGuideline(!0),Ce.interactiveLayer.tooltip.contentGenerator((e=>(0,$.HO)(e,Be,i)))}Ce.width(Fe),Ce.height(Le),r.datum(a).transition().duration(500).attr("height",Le).attr("width",Fe).call(Ce),ve&&Ce.yAxis.tickFormat((e=>0!==e&&Math.log10(e)%1==0?ze(e):"")),Se>0&&r.select(".nv-x.nv-axis > g").selectAll("g").selectAll("text").attr("dx",-6.5);const Ge=()=>{if(Ce.yDomain&&Array.isArray(pe)&&2===pe.length){const[e,t]=pe,i=(0,w.Z)(e)&&!Number.isNaN(e),s=(0,w.Z)(t)&&!Number.isNaN(t);if((i||s)&&"area"===oe&&"expand"===Ce.style())Ce.yDomain([0,1]);else if((i||s)&&"area"===oe&&"stream"===Ce.style())Ce.yDomain((0,$.po)(a));else if(i&&s)Ce.yDomain([e,t]),Ce.clipEdge(!0);else if(i||s){let[o,r]=[0,1];"area"===oe||De(["bar","dist_bar"])&&Ce.stacked()?[o,r]=(0,$.po)(a):[o,r]=(0,$.tH)(a);const n=i?e:o,l=s?t:r;Ce.yDomain([n,l]),Ce.clipEdge(!0)}}};if(Ge(),Ce.dispatch&&Ce.dispatch.stateChange&&Ce.dispatch.on("stateChange.applyYAxisBounds",Ge),De(["dual_line","line_multi"])){const e=Ce.yAxis1.ticks(),t=Ce.yAxis1.scale().domain(Ce.yAxis1.domain()).nice(e).ticks(e),a=Ce.yAxis2.scale().domain(Ce.yAxis2.domain()).nice(e).ticks(e),i=t.length-a.length;if(t.length>0&&a.length>0&&0!==i){const e=i<0?t:a,s=e[1]-e[0];for(let t=0;t<Math.abs(i);t+=1)t%2==0?e.unshift(e[0]-s):e.push(e[e.length-1]+s);Ce.yDomain1([t[0],t[t.length-1]]),Ce.yDomain2([a[0],a[a.length-1]]),Ce.yAxis1.tickValues(t),Ce.yAxis2.tickValues(a)}Ce.yDomain1([pe[0]||t[0],pe[1]||t[t.length-1]]),Ce.yDomain2([xe[0]||a[0],xe[1]||a[a.length-1]])}if(ae&&(r.selectAll(".nv-point").style("stroke-opacity",1).style("fill-opacity",1),Ce.dispatch.on("stateChange.showMarkers",(()=>{setTimeout((()=>{r.selectAll(".nv-point").style("stroke-opacity",1).style("fill-opacity",1)}),10)}))),void 0!==Ce.yAxis||void 0!==Ce.yAxis2){const t=Math.ceil(Math.min(i*(we?.01:.03),30)),s=Ce.margin();Ce.xAxis&&(s.bottom=28);const n=(0,$.GF)(r,Ce.yAxis2?"nv-y1":"nv-y"),c=(0,$.GF)(r,"nv-x");if(s.left=n+t,ge&&""!==ge&&(s.left+=25),Q&&(s.top+=24),ce&&(s.right=Math.max(20,c/2)+t),45===Se?(s.bottom=c*Math.sin(Math.PI*Se/180)+t+30,s.right=c*Math.cos(Math.PI*Se/180)+t):Oe&&(s.bottom=40),De(["dual_line","line_multi"])){const e=(0,$.GF)(r,"nv-y2");s.right=e+t}if(m&&"auto"!==m&&(s.bottom=parseInt(m,10)),O&&"auto"!==O&&(s.left=O),le&&""!==le&&Ce.xAxis){s.bottom+=25;let e=0;s.bottom&&!Number.isNaN(s.bottom)&&(e=s.bottom-45),Ce.xAxis.axisLabel(le).axisLabelDistance(e)}if(ge&&""!==ge&&Ce.yAxis){let e=0;s.left&&!Number.isNaN(s.left)&&(e=s.left-70),Ce.yAxis.axisLabel(ge).axisLabelDistance(e)}if($e&&o&&Me.length>0){const e=Me.filter((e=>e.annotationType===M.ZP.TIME_SERIES)).reduce(((e,t)=>e.concat((o[t.name]||[]).map((e=>{if(!e)return{};const a=Array.isArray(e.key)?`${t.name}, ${e.key.join(", ")}`:`${t.name}, ${e.key}`;return{...e,key:a,color:t.color,strokeWidth:t.width,classed:`${t.opacity} ${t.style} nv-timeseries-annotation-layer showMarkers${t.showMarkers} hideLine${t.hideLine}`}})))),[]);a.push(...e)}if(Te&&(Ce&&Ce.interactiveLayer&&Ce.interactiveLayer.tooltip&&Ce.interactiveLayer.tooltip.classes([(0,$.T7)(Te)]),Ce&&Ce.tooltip&&Ce.tooltip.classes([(0,$.T7)(Te)])),Ce.margin(s),r.datum(a).transition().duration(500).attr("width",Fe).attr("height",Le).call(Ce),window.addEventListener("scroll",l()((()=>(0,$.Vl)(!1)),250)),$e&&Me.length>0){const t=Me.filter((e=>e.annotationType===M.ZP.FORMULA));let i,s,n;if("bar"===oe?(s=y().min(a[0].values,(e=>e.x)),i=y().max(a[0].values,(e=>e.x)),n=y().scale.quantile().domain([s,i]).range(Ce.xAxis.range())):(s=Ce.xAxis.scale().domain()[0].valueOf(),i=Ce.xAxis.scale().domain()[1].valueOf(),n=Ce.xScale?Ce.xScale():Ce.xAxis.scale?Ce.xAxis.scale():y().scale.linear()),n&&n.clamp&&n.clamp(!0),t.length>0){const e=[];if("bar"===oe){const t=a.reduce(((e,t)=>(t.values.forEach((t=>e.add(t.x))),e)),new Set);e.push(...t.values()),e.sort()}else{let t=Math.min(...a.map((e=>Math.min(...e.values.slice(1).map(((t,a)=>t.x-e.values[a].x))))));const o=(i-s)/(t||1);t=o<100?(i-s)/100:t,t=o>500?(i-s)/500:t,e.push(s);for(let a=s;a<i;a+=t)e.push(a);e.push(i)}const o=t.map((t=>{const{value:a}=t;return{key:t.name,values:e.map((e=>({x:e,y:(0,L.f)(a,e)}))),color:t.color,strokeWidth:t.width,classed:`${t.opacity} ${t.style}`}}));a.push(...o)}const l=Ce.xAxis1?Ce.xAxis1:Ce.xAxis,c=Ce.yAxis1?Ce.yAxis1:Ce.yAxis,h=l.scale().range()[1],m=c.scale().range()[0];o&&(Me.filter((e=>e.annotationType===M.ZP.EVENT&&o&&o[e.name])).forEach(((t,a)=>{const i=(0,M.yb)(t),s=y().select(e).select(".nv-wrap").append("g").attr("class",`nv-event-annotation-layer-${a}`),r=i.color||z((0,$.gO)(i.name),u),l=(0,$.Gr)({...i,annotationTipClass:`arrow-down nv-event-annotation-layer-${t.sourceType}`}),c=(o[i.name].records||[]).map((e=>{const t=new Date(d().utc(e[i.timeColumn]));return{...e,[i.timeColumn]:t}})).filter((e=>!Number.isNaN(e[i.timeColumn].getMilliseconds())));c.length>0&&s.selectAll("line").data(c).enter().append("line").attr({x1:e=>n(new Date(e[i.timeColumn])),y1:0,x2:e=>n(new Date(e[i.timeColumn])),y2:m}).attr("class",`${i.opacity} ${i.style}`).style("stroke",r).style("stroke-width",i.width).on("mouseover",l.show).on("mouseout",l.hide).call(l),Ce.focus&&Ce.focus.dispatch.on("onBrush.event-annotation",(()=>{s.selectAll("line").data(c).attr({x1:e=>n(new Date(e[i.timeColumn])),y1:0,x2:e=>n(new Date(e[i.timeColumn])),y2:m,opacity:e=>{const t=n(new Date(e[i.timeColumn]));return t>0&&t<h?1:0}})}))})),Me.filter((e=>e.annotationType===M.ZP.INTERVAL&&o&&o[e.name])).forEach(((t,a)=>{const i=(0,M.yb)(t),s=y().select(e).select(".nv-wrap").append("g").attr("class",`nv-interval-annotation-layer-${a}`),r=i.color||z((0,$.gO)(i.name),u),l=(0,$.Gr)(i),c=(o[i.name].records||[]).map((e=>{const t=new Date(d().utc(e[i.timeColumn])),a=new Date(d().utc(e[i.intervalEndColumn]));return{...e,[i.timeColumn]:t,[i.intervalEndColumn]:a}})).filter((e=>!Number.isNaN(e[i.timeColumn].getMilliseconds())&&!Number.isNaN(e[i.intervalEndColumn].getMilliseconds())));c.length>0&&s.selectAll("rect").data(c).enter().append("rect").attr({x:e=>Math.min(n(new Date(e[i.timeColumn])),n(new Date(e[i.intervalEndColumn]))),y:0,width:e=>Math.max(Math.abs(n(new Date(e[i.intervalEndColumn]))-n(new Date(e[i.timeColumn]))),1),height:m}).attr("class",`${i.opacity} ${i.style}`).style("stroke-width",i.width).style("stroke",r).style("fill",r).style("fill-opacity",.2).on("mouseover",l.show).on("mouseout",l.hide).call(l),Ce.focus&&Ce.focus.dispatch.on("onBrush.interval-annotation",(()=>{s.selectAll("rect").data(c).attr({x:e=>n(new Date(e[i.timeColumn])),width:e=>{const t=n(new Date(e[i.timeColumn]));return n(new Date(e[i.intervalEndColumn]))-t}})}))}))),r.datum(a).attr("height",Le).attr("width",Fe).call(Ce),Ce.dispatch.on("renderEnd.timeseries-annotation",(()=>{y().selectAll(".slice_container .nv-timeseries-annotation-layer.showMarkerstrue .nv-point").style("stroke-opacity",1).style("fill-opacity",1),y().selectAll(".slice_container .nv-timeseries-annotation-layer.hideLinetrue").style("stroke-width",0)}))}}return(0,$.Aw)(Ce),Ce}))}V.displayName="NVD3",V.propTypes=R;const H=V;var U=a(11965);const W=(0,i.Z)(H,{componentWillUnmount:function(){const{id:e}=this.props;null!=e?(0,$.o2)(e):(0,$.Vl)(!0)}}),q=({className:e,...t})=>(0,U.tZ)("div",{className:e},(0,U.tZ)(W,t));q.propTypes={className:r().string.isRequired};const J=(0,s.iK)(q)`
  .superset-legacy-chart-nvd3-dist-bar,
  .superset-legacy-chart-nvd3-bar {
    overflow-x: auto !important;
    svg {
      &.nvd3-svg {
        width: auto;
        font-size: ${({theme:e})=>e.typography.sizes.m};
      }
    }
  }
  .superset-legacy-chart-nvd3 {
    nv-x text {
      font-size: ${({theme:e})=>e.typography.sizes.m};
    }
    g.superset path {
      stroke-dasharray: 5, 5;
    }
    .nvtooltip tr.highlight td {
      font-weight: ${({theme:e})=>e.typography.weights.bold};
      font-size: ${({theme:e})=>e.typography.sizes.m}px !important;
    }
    text.nv-axislabel {
      font-size: ${({theme:e})=>e.typography.sizes.m} !important;
    }
    g.solid path,
    line.solid {
      stroke-dasharray: unset;
    }
    g.dashed path,
    line.dashed {
      stroke-dasharray: 5, 5;
    }
    g.longDashed path,
    line.dotted {
      stroke-dasharray: 1, 1;
    }

    g.opacityLow path,
    line.opacityLow {
      stroke-opacity: 0.2;
    }

    g.opacityMedium path,
    line.opacityMedium {
      stroke-opacity: 0.5;
    }
    g.opacityHigh path,
    line.opacityHigh {
      stroke-opacity: 0.8;
    }
    g.time-shift-0 path,
    line.time-shift-0 {
      stroke-dasharray: 5, 5;
    }
    g.time-shift-1 path,
    line.time-shift-1 {
      stroke-dasharray: 1, 5;
    }
    g.time-shift-2 path,
    line.time-shift-3 {
      stroke-dasharray: 5, 1;
    }
    g.time-shift-3 path,
    line.time-shift-3 {
      stroke-dasharray: 5, 1;
    }
    g.time-shift-4 path,
    line.time-shift-4 {
      stroke-dasharray: 5, 10;
    }
    g.time-shift-5 path,
    line.time-shift-5 {
      stroke-dasharray: 0.9;
    }
    g.time-shift-6 path,
    line.time-shift-6 {
      stroke-dasharray: 15, 10, 5;
    }
    g.time-shift-7 path,
    line.time-shift-7 {
      stroke-dasharray: 15, 10, 5, 10;
    }
    g.time-shift-8 path,
    line.time-shift-8 {
      stroke-dasharray: 15, 10, 5, 10, 15;
    }
    g.time-shift-9 path,
    line.time-shift-9 {
      stroke-dasharray: 5, 5, 1, 5;
    }
    .nv-noData.body {
      font-size: ${({theme:e})=>e.typography.sizes.m};
      font-weight: ${({theme:e})=>e.typography.weights.normal};
    }
  }
  .superset-legacy-chart-nvd3-tr-highlight {
    border-top: 1px solid;
    border-bottom: 1px solid;
    font-weight: ${({theme:e})=>e.typography.weights.bold};
  }
  .superset-legacy-chart-nvd3-tr-total {
    font-weight: ${({theme:e})=>e.typography.weights.bold};
  }
  .nvtooltip {
    .tooltip-header {
      white-space: nowrap;
      font-weight: ${({theme:e})=>e.typography.weights.bold};
    }
    tbody tr:not(.tooltip-header) td:nth-child(2) {
      word-break: break-word;
    }
  }
  .d3-tip.nv-event-annotation-layer-table,
  .d3-tip.nv-event-annotation-layer-NATIVE {
    width: 200px;
    border-radius: 2px;
    background-color: ${({theme:e})=>e.colors.grayscale.base};
    fill-opacity: 0.6;
    margin: ${({theme:e})=>2*e.gridUnit}px;
    padding: ${({theme:e})=>2*e.gridUnit}px;
    color: ${({theme:e})=>e.colors.grayscale.light5};
    &:after {
      content: '\\25BC';
      font-size: ${({theme:e})=>e.typography.sizes.m};
      color: ${({theme:e})=>e.colors.grayscale.base};
      position: absolute;
      bottom: -14px;
      left: 94px;
    }
  }
`}}]);
//# sourceMappingURL=bdc3d073b580f9a64a8b.chunk.js.map
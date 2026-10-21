"""Self-contained circuit viewer: fit, zoom, and scroll with no CDN assets."""


def viewer_html(svg):
    return '''<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RTL Studio — Circuit explorer</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0e1726;color:#e2e8f0;font:14px system-ui}
header{height:52px;display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid #334155}
button{background:#19283b;color:#e2e8f0;border:1px solid #47617c;border-radius:6px;padding:7px 12px;cursor:pointer}
button:hover{border-color:#2dd4bf}button:focus-visible{outline:2px solid #2dd4bf}
#status{font-variant-numeric:tabular-nums;color:#94a3b8;margin-left:6px}
#viewport{height:calc(100vh - 52px);overflow:auto;overscroll-behavior:contain}
svg{display:block;max-width:none!important;flex-shrink:0}
</style></head><body>
<header><button id="fit">Fit circuit</button><button id="out" aria-label="Zoom out">−</button>
<button id="in" aria-label="Zoom in">+</button><button id="actual">100%</button><span id="status" aria-live="polite"></span></header>
<div id="viewport">''' + svg + '''</div>
<script>
const viewport=document.getElementById('viewport'),svg=viewport.querySelector('svg');
const box=svg.viewBox.baseVal,W=box.width,H=box.height;
let scale=1,fitted=true;
function resize(next,center=true){
 const cx=(viewport.scrollLeft+viewport.clientWidth/2)/scale;
 const cy=(viewport.scrollTop+viewport.clientHeight/2)/scale;
 scale=Math.max(.01,Math.min(5,next));
 svg.setAttribute('width',W*scale);svg.setAttribute('height',H*scale);
 document.getElementById('status').textContent=Math.round(scale*100)+'%';
 if(center){viewport.scrollLeft=cx*scale-viewport.clientWidth/2;viewport.scrollTop=cy*scale-viewport.clientHeight/2;}
}
function fit(){fitted=true;resize(Math.min((viewport.clientWidth-24)/W,(viewport.clientHeight-24)/H),false);viewport.scrollTo(0,0);}
function zoom(factor){fitted=false;resize(scale*factor);}
document.getElementById('fit').onclick=fit;
document.getElementById('in').onclick=()=>zoom(1.25);
document.getElementById('out').onclick=()=>zoom(.8);
document.getElementById('actual').onclick=()=>{fitted=false;resize(1);};
viewport.addEventListener('wheel',event=>{if(event.ctrlKey||event.metaKey){event.preventDefault();zoom(event.deltaY<0?1.1:1/1.1);}},{passive:false});
window.addEventListener('resize',()=>{if(fitted)fit();});
requestAnimationFrame(fit);
</script></body></html>'''

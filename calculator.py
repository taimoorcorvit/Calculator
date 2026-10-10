import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# Tighten Streamlit's default padding so the calculator sits at the top
st.markdown(
    """
    <style>
      .block-container {padding: .6rem 1rem 0 1rem !important; max-width: 460px;}
      .stApp iframe {height: min(660px, calc(100vh - 90px)) !important;}
      header[data-testid="stHeader"] {display: none;}
      footer {visibility: hidden;}
      .dev-title {text-align:center; font-size:.95rem; font-weight:600; margin-bottom:.35rem; white-space:nowrap;}
      .dev-title span {color:#3b6fe0;}
    </style>
    <div class="dev-title">Scientific Calculator &mdash; Developed by <span>Taimoor Jan</span></div>
    """,
    unsafe_allow_html=True,
)

CALC_HTML = r"""
<style>
  :root{
    --bg:#f7f7f7; --fn:#e6eaf5; --num:#ffffff; --op:#dcdcdc; --eq:#4d8dfc;
    --txt:#2b2b2b; --muted:#8a8a8a; --red:#e0584f; --accent:#3b6fe0;
  }
  @media (prefers-color-scheme: dark){
    :root{ --bg:#1c1c1e; --fn:#2c3040; --num:#2a2a2d; --op:#3a3a3d; --txt:#f1f1f1; --muted:#9a9a9a; }
  }
  *{box-sizing:border-box; -webkit-tap-highlight-color:transparent; user-select:none;}
  html,body{height:100%;} body{margin:0; font-family:'Google Sans','Segoe UI',Roboto,Arial,sans-serif; background:transparent;}
  #phone{
    width:100%; max-width:340px; height:100%; max-height:640px; margin:0 auto; background:var(--bg);
    border-radius:24px; padding:12px 12px 14px; display:flex; flex-direction:column;
    box-shadow:0 6px 24px rgba(0,0,0,.18); outline:none; position:relative; overflow:hidden;
  }
  #top{display:flex; justify-content:space-between; align-items:center; padding:6px 8px;}
  .icon{background:none; border:none; cursor:pointer; color:var(--txt); font-size:24px; padding:6px 10px; border-radius:12px;}
  .icon:hover{background:rgba(128,128,128,.15);}
  #screen{flex:1; display:flex; flex-direction:column; justify-content:flex-end; align-items:flex-end; padding:0 10px 12px; min-height:0;}
  #expr{font-size:44px; color:var(--txt); text-align:right; width:100%; word-break:break-all; line-height:1.1; min-height:48px;}
  #expr .op{color:var(--accent);}
  #res{font-size:26px; color:var(--muted); margin-top:16px; min-height:34px; text-align:right; width:100%; word-break:break-all;}
  #res.err{color:var(--red); font-size:18px;}
  #keys{display:grid; grid-template-columns:repeat(4,1fr); grid-template-rows:repeat(9,1fr); gap:8px; flex:0 0 72%; min-height:0;}
  button.k{
    height:100%; min-height:0; border:none; border-radius:999px; font-size:18px; cursor:pointer;
    color:var(--txt); background:var(--num); box-shadow:0 1px 3px rgba(0,0,0,.12);
    transition:transform .06s, filter .15s; font-family:inherit;
  }
  button.k:active{transform:scale(.94); filter:brightness(.92);}
  button.fn{background:var(--fn); font-size:15px;}
  button.op{background:var(--op); font-size:22px;}
  button.clr{color:var(--red);}
  button.eq{background:var(--eq); color:#fff; font-size:24px;}
  button.k.flash{filter:brightness(.8); transform:scale(.94);}
  #hist{
    position:absolute; inset:0; background:var(--bg); padding:18px; display:none; flex-direction:column; z-index:5;
  }
  #hist h3{margin:0 0 10px; color:var(--txt); font-weight:600;}
  #hlist{flex:1; overflow:auto; color:var(--txt);}
  .h{padding:10px 4px; border-bottom:1px solid rgba(128,128,128,.25); text-align:right; cursor:pointer;}
  .h small{display:block; color:var(--muted); font-size:15px;}
  .h b{font-size:22px; font-weight:500;}
  #hbar{display:flex; justify-content:space-between; margin-top:10px;}
  #hbar button{border:none; background:var(--fn); color:var(--txt); padding:10px 18px; border-radius:20px; cursor:pointer; font-size:15px;}
  #hint{font-size:11px; color:var(--muted); text-align:center; margin-top:8px;}
</style>

<div id="phone" tabindex="0">
  <div id="screen">
    <div id="expr"></div>
    <div id="res"></div>
  </div>
  <div id="keys"></div>

</div>

<script>
(function(){
  let expr = "";          // display expression
  let justEvaluated = false;
  let deg = true;         // degrees by default; toggle with button
  let history = [];

  const exprEl = document.getElementById('expr');
  const resEl  = document.getElementById('res');
  const keysEl = document.getElementById('keys');
  const phone  = document.getElementById('phone');

  // [label, action, css-class, keyboard-id]
  const layout = [
    ['⇄','inv','fn'], ['Rad','mode','fn'], ['√','√(','fn'], ['|x|','abs(','fn'],
    ['sin','sin(','fn'], ['cos','cos(','fn'], ['tan','tan(','fn'], ['π','π','fn'],
    ['ln','ln(','fn'], ['log','log(','fn'], ['1/x','recip','fn'], ['e','e','fn'],
    ['eˣ','exp','fn'], ['x²','sq','fn'], ['xʸ','^','fn'], ['+/−','neg','fn'],
    ['C','clear','clr'], ['⌫','back',''], ['%','%',''], ['÷','÷','op'],
    ['7','7',''], ['8','8',''], ['9','9',''], ['×','×','op'],
    ['4','4',''], ['5','5',''], ['6','6',''], ['−','−','op'],
    ['1','1',''], ['2','2',''], ['3','3',''], ['+','+','op'],
    ['( )','paren',''], ['0','0',''], ['.','.',''], ['=','eq','eq'],
  ];

  const btnByAction = {};
  layout.forEach(([label, act, cls]) => {
    const b = document.createElement('button');
    b.className = 'k ' + cls;
    b.textContent = label;
    b.dataset.act = act;
    b.onclick = () => { press(act); };
    keysEl.appendChild(b);
    btnByAction[act] = b;
  });
  // The first fn key is a decorative "inverse" toggle: swaps sin/cos/tan -> asin/acos/atan etc.
  let inverse = false;
  const invMap = {'sin(':'asin(','cos(':'acos(','tan(':'atan(','ln(':'ln(','log(':'log('};
  function refreshLabels(){
    const set = (act, a, b) => { btnByAction[act].textContent = inverse ? b : a; };
    ['sin','cos','tan'].forEach(f => {
      const b = btnByAction[f+'('];
      b.textContent = inverse ? 'a'+f : f;
    });
    btnByAction['mode'].textContent = deg ? 'Deg' : 'Rad';
  }
  refreshLabels();

  function flash(act){
    const b = btnByAction[act]; if(!b) return;
    b.classList.add('flash'); setTimeout(()=>b.classList.remove('flash'), 110);
  }

  // ---------- Tokenizer / evaluator (no eval of raw input) ----------
  const FUNCS = ['asin','acos','atan','sin','cos','tan','ln','log','abs'];
  function tokenize(s){
    const tokens = [];
    let i = 0;
    while(i < s.length){
      const c = s[i];
      if(c === ' '){ i++; continue; }
      let m = s.slice(i).match(/^(\d+\.?\d*|\.\d+)/);
      if(m){ tokens.push({t:'num', v:m[0]}); i += m[0].length; continue; }
      let found = false;
      for(const f of FUNCS){
        if(s.startsWith(f, i)){ tokens.push({t:'fn', v:f}); i += f.length; found = true; break; }
      }
      if(found) continue;
      if(c === '√'){ tokens.push({t:'fn', v:'sqrt'}); i++; continue; }
      if(c === 'π'){ tokens.push({t:'const', v:'PI'}); i++; continue; }
      if(c === 'e'){ tokens.push({t:'const', v:'E'}); i++; continue; }
      if('+−-×*÷/^'.includes(c)){ tokens.push({t:'bin', v:c}); i++; continue; }
      if(c === '('){ tokens.push({t:'(', v:'('}); i++; continue; }
      if(c === ')'){ tokens.push({t:')', v:')'}); i++; continue; }
      if(c === '%'){ tokens.push({t:'pct', v:'%'}); i++; continue; }
      throw new Error('Invalid input');
    }
    return tokens;
  }

  // Recursive-descent parser
  function evaluate(src){
    const tokens = tokenize(src);
    // auto-close open parentheses
    let open = 0;
    tokens.forEach(t => { if(t.t==='(' || t.t==='fn') { if(t.t==='(') open++; } if(t.t===')') open--; });
    // functions are always followed by "(" token in our input, so counting "(" is enough
    while(open-- > 0) tokens.push({t:')', v:')'});

    let p = 0;
    const peek = () => tokens[p];
    const next = () => tokens[p++];
    const toRad = x => deg ? x*Math.PI/180 : x;
    const fromRad = x => deg ? x*180/Math.PI : x;

    function expression(){
      let v = term();
      while(peek() && peek().t==='bin' && (peek().v==='+' || peek().v==='−' || peek().v==='-')){
        const op = next().v;
        const r = term();
        v = (op==='+') ? v + r : v - r;
      }
      return v;
    }
    function term(){
      let v = power();
      while(peek()){
        const t = peek();
        if(t.t==='bin' && (t.v==='×' || t.v==='*' || t.v==='÷' || t.v==='/')){
          next(); const r = power();
          if(t.v==='÷' || t.v==='/'){
            if(r === 0) throw new Error("Can't divide by 0");
            v = v / r;
          } else v = v * r;
        } else if(t.t==='num' || t.t==='(' || t.t==='fn' || t.t==='const'){
          v = v * power(); // implicit multiplication
        } else break;
      }
      return v;
    }
    function power(){
      let base = unary();
      if(peek() && peek().t==='bin' && peek().v==='^'){
        next();
        const exp = power(); // right-associative
        return Math.pow(base, exp);
      }
      return base;
    }
    function unary(){
      const t = peek();
      if(t && t.t==='bin' && (t.v==='−' || t.v==='-')){ next(); return -unary(); }
      if(t && t.t==='bin' && t.v==='+'){ next(); return unary(); }
      return postfix();
    }
    function postfix(){
      let v = primary();
      while(peek() && peek().t==='pct'){ next(); v = v/100; }
      return v;
    }
    function primary(){
      const t = next();
      if(!t) throw new Error('Incomplete expression');
      if(t.t==='num') return parseFloat(t.v);
      if(t.t==='const') return t.v==='PI' ? Math.PI : Math.E;
      if(t.t==='('){
        const v = expression();
        if(peek() && peek().t===')') next();
        return v;
      }
      if(t.t==='fn'){
        if(!peek() || peek().t!=='(') throw new Error('Invalid input');
        next();
        const a = expression();
        if(peek() && peek().t===')') next();
        switch(t.v){
          case 'sin': { const r = Math.sin(toRad(a)); return Math.abs(r) < 1e-15 ? 0 : r; }
          case 'cos': { const r = Math.cos(toRad(a)); return Math.abs(r) < 1e-15 ? 0 : r; }
          case 'tan': {
            const c = Math.cos(toRad(a));
            if(Math.abs(c) < 1e-15) throw new Error('Undefined');
            const r = Math.tan(toRad(a)); return Math.abs(r) < 1e-15 ? 0 : r;
          }
          case 'asin': if(a<-1||a>1) throw new Error('Invalid input'); return fromRad(Math.asin(a));
          case 'acos': if(a<-1||a>1) throw new Error('Invalid input'); return fromRad(Math.acos(a));
          case 'atan': return fromRad(Math.atan(a));
          case 'ln':   if(a<=0) throw new Error('Invalid input'); return Math.log(a);
          case 'log':  if(a<=0) throw new Error('Invalid input'); return Math.log10(a);
          case 'sqrt': if(a<0) throw new Error('Invalid input'); return Math.sqrt(a);
          case 'abs':  return Math.abs(a);
        }
      }
      throw new Error('Invalid input');
    }

    const result = expression();
    if(p < tokens.length) throw new Error('Invalid input');
    return result;
  }

  function fmt(n){
    if(!isFinite(n)) throw new Error('Invalid input');
    if(Math.abs(n) >= 1e15 || (Math.abs(n) < 1e-9 && n !== 0)){
      return n.toExponential(8).replace(/\.?0+e/, 'e').replace('e+','e');
    }
    let s = parseFloat(n.toPrecision(12)).toString();
    return s.replace('-', '−');
  }

  // ---------- Rendering ----------
  function render(){
    // highlight operators in blue like the screenshot
    const html = expr.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))
                     .replace(/([+−×÷^])/g, '<span class="op">$1</span>');
    exprEl.innerHTML = html || '&nbsp;';
    const len = expr.length;
    exprEl.style.fontSize = len > 22 ? '22px' : len > 15 ? '28px' : len > 9 ? '36px' : '44px';
    resEl.classList.remove('err');
    if(!expr){ resEl.textContent = ''; return; }
    try{
      const v = evaluate(expr);
      const f = fmt(v);
      resEl.textContent = (f === expr) ? '' : f;
    }catch(e){
      resEl.textContent = '';
    }
  }

  // ---------- Actions ----------
  const isOpChar = c => '+−×÷^'.includes(c);

  function append(txt){
    if(justEvaluated){
      // starting with a number/function starts fresh; starting with an operator continues
      if(!(isOpChar(txt[0]) || txt === '%')) expr = '';
      justEvaluated = false;
    }
    expr += txt;
  }

  function press(act){
    flash(act);
    switch(act){
      case 'clear': expr = ''; justEvaluated = false; break;
      case 'back':
        if(justEvaluated){ justEvaluated = false; }
        // remove whole function token if cursor is right after "name("
        const m = expr.match(/(asin\(|acos\(|atan\(|sin\(|cos\(|tan\(|ln\(|log\(|abs\(|√\()$/);
        expr = m ? expr.slice(0, -m[0].length) : expr.slice(0, -1);
        break;
      case 'eq': doEquals(); return;
      case 'inv': inverse = !inverse; refreshLabels(); return;
      case 'mode': deg = !deg; refreshLabels(); break;
      case 'sin(': case 'cos(': case 'tan(':
        append(inverse ? 'a'+act : act); break;
      case 'paren': {
        const o = (expr.match(/\(/g)||[]).length, c = (expr.match(/\)/g)||[]).length;
        const last = expr.slice(-1);
        if(justEvaluated){ justEvaluated=false; }
        if(o > c && last && !isOpChar(last) && last !== '(') expr += ')';
        else {
          // implicit multiplication handled by parser
          expr += '(';
        }
        break;
      }
      case 'recip': append('1÷('); break;
      case 'sq': if(expr) { justEvaluated=false; expr += '^2'; } break;
      case 'exp': append('e^('); break;
      case 'neg': {
        if(justEvaluated) justEvaluated = false;
        const mm = expr.match(/\(−(\d+\.?\d*)\)$/);
        if(mm){ expr = expr.slice(0, -mm[0].length) + mm[1]; }
        else {
          const n = expr.match(/(\d+\.?\d*)$/);
          if(n) expr = expr.slice(0, -n[0].length) + '(−' + n[0] + ')';
          else if(!expr) expr = '−';
        }
        break;
      }
      case '.': {
        const last = expr.split(/[+−×÷^()%]/).pop();
        if(last.includes('.')) break;
        append(last === '' ? '0.' : '.');
        break;
      }
      case '+': case '−': case '×': case '÷': case '^': {
        if(!expr && act !== '−') break;
        const last = expr.slice(-1);
        if(isOpChar(last)) expr = expr.slice(0,-1);  // replace operator
        if(justEvaluated) justEvaluated = false;
        expr += act;
        break;
      }
      default: append(act);
    }
    render();
  }

  function doEquals(){
    if(!expr) return;
    try{
      const v = evaluate(expr);
      const out = fmt(v);
      history.unshift({e: expr, r: out});
      if(history.length > 50) history.pop();
      expr = out;
      justEvaluated = true;
      render();
      resEl.textContent = '';
    }catch(e){
      resEl.textContent = e.message;
      resEl.classList.add('err');
    }
  }

  // ---------- Keyboard ----------
  const keyMap = {
    '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
    '.':'.', ',':'.', '+':'+', '-':'−', '*':'×', 'x':'×', 'X':'×', '/':'÷', '^':'^', '%':'%',
    '(':'(', ')':')', 's':'sin(', 'o':'cos(', 't':'tan(', 'l':'log(', 'n':'ln(', 'r':'√(', 'p':'π', 'e':'e',
  };
  function onKey(ev){
    if(ev.ctrlKey || ev.metaKey || ev.altKey) return;
    const tgt = ev.target;
    if(tgt && tgt.tagName && ['INPUT','TEXTAREA'].includes(tgt.tagName) ) return; // don't hijack other inputs
    const k = ev.key;
    let handled = true;
    if(k === 'Enter' || k === '='){ press('eq'); }
    else if(k === 'Backspace'){ press('back'); }
    else if(k === 'Escape' || k === 'Delete'){ press('clear'); }
    else if(k === '(' || k === ')'){ if(k==='('){ flash('paren'); append('('); render(); } else { flash('paren'); expr += ')'; justEvaluated=false; render(); } }
    else if(keyMap[k]){
      const a = keyMap[k];
      if(a === 'sin(' || a === 'cos(' || a === 'tan(') { press(a); }
      else if(['√(','log(','ln(','π','e'].includes(a)){ flash(a==='π'?'π':a==='e'?'e':a); append(a); render(); }
      else press(a);
    }
    else handled = false;
    if(handled){ ev.preventDefault(); ev.stopPropagation(); }
  }

  // Listen inside the iframe AND on the parent Streamlit page so typing works without clicking first
  try{
    const par = window.parent;
    if(par.__sciCalcHandler){ par.document.removeEventListener('keydown', par.__sciCalcHandler, true); }
    par.__sciCalcHandler = onKey;
    par.document.addEventListener('keydown', onKey, true);
  }catch(e){ /* cross-origin fallback: iframe-only */ }
  document.addEventListener('keydown', onKey, true);
  phone.addEventListener('click', () => phone.focus());
  window.addEventListener('load', () => phone.focus());
  phone.focus();

  render();
})();
</script>
"""

components.html(CALC_HTML, height=660, scrolling=False)
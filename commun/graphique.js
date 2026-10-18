/* Graphique de fonction réutilisable (T19) : dessin d'une courbe, de ses asymptotes, de ses extrema et de ses trous
   sur un <canvas>, à échelle égale en x et en y.

   Le dessin ne mesure aucun texte (pas de measureText) : tout ce qu'il écrit sur le canvas se déduit de la fenêtre et des
   données, donc la même suite d'appels sur toutes les machines (tests/pages/graphique.py enregistre et compare cette trace).

   dessinerGraphique(canvas, g, extrema, asymptotes, vista, forcerClair)
     g            { xmin, xmax, ymin, ymax, segments }   segments : listes de [x, y] ; y = null lève le crayon
     extrema      [{ x_val, f_val }]                     points pleins, avec leurs coordonnées écrites à côté
     asymptotes   [{ genre, … }]                         horizontale, verticale, oblique (pointillé) ; trou (rond vide)
     vista        fenêtre voulue { xmin, xmax, ymin, ymax } (zoom, déplacement) ; g si absente
     forcerClair  couleurs du thème clair quel que soit le thème de l'écran (juste avant l'impression)
   Laisse dans canvas.__rendu la fenêtre réellement affichée (après correction d'aspect) : x/y min/max, échelle, marges. */

export function joliPas(etendue){
  const brut=etendue/8, exp=Math.floor(Math.log10(brut)), base=brut/Math.pow(10,exp);
  const nice=base<1.5?1:base<3?2:base<7?5:10;
  return nice*Math.pow(10,exp);
}
export function etiquette(v){
  const r=Math.round(v*100)/100;
  if(Math.abs(r)<1e-9) return "0";
  return Number.isInteger(r) ? String(r) : String(r.toFixed(2)).replace(/0+$/,"").replace(/\.$/,"");
}
export function fleche(ctx, x, y, angle){
  const t=7;
  ctx.save(); ctx.translate(x,y); ctx.rotate(angle);
  ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(-t,t*0.45); ctx.lineTo(-t,-t*0.45); ctx.closePath(); ctx.fill();
  ctx.restore();
}
export function dessinerGraphique(canvas, g, extrema, asymptotes, vista, forcerClair){
  const dpr=window.devicePixelRatio||1;
  const rect=canvas.getBoundingClientRect();
  const W=rect.width||640, H=rect.height||380;
  canvas.width=W*dpr; canvas.height=H*dpr;
  const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr); ctx.clearRect(0,0,W,H);

  const padL=14,padR=28,padT=24,padB=14;
  const availW=W-padL-padR, availH=H-padT-padB;

  // Cadrage à échelle égale en x et y (comme GeoGebra) : `vista` est la fenêtre
  // de données qu'on veut voir (après zoom/déplacement) ; on l'étend sur l'axe
  // le plus "serré" pour que 1 unité fasse le même nombre de pixels horizontalement
  // et verticalement — sinon les pentes (ex. une asymptote oblique à 45°) seraient
  // faussées.
  const boite=vista||g;
  const cx=(boite.xmin+boite.xmax)/2, cy=(boite.ymin+boite.ymax)/2;
  const rx=Math.max((boite.xmax-boite.xmin)/2, 1e-6), ry=Math.max((boite.ymax-boite.ymin)/2, 1e-6);
  const echelle=Math.min(availW/(2*rx), availH/(2*ry));
  const rx2=availW/(2*echelle), ry2=availH/(2*echelle);
  const xmin=cx-rx2, xmax=cx+rx2, ymin=cy-ry2, ymax=cy+ry2;
  canvas.__rendu={xmin,xmax,ymin,ymax,echelle,padL,padT,availH};

  const X=x=>padL+(x-xmin)*echelle;
  const Y=y=>padT+availH-(y-ymin)*echelle;

  let colFg,colMuted,colGrid,colAccent,colGood,colBg;
  if(forcerClair){
    colFg="#1b2130"; colMuted="#5b6478"; colGrid="#d6dbe6"; colAccent="#1f4e79";
    colGood="#17784a"; colBg="#f3f6fb";
  } else {
    const cs=getComputedStyle(document.documentElement);
    const col=n=>(cs.getPropertyValue(n)||"").trim();
    colFg=col("--fg")||"#1b2130"; colMuted=col("--muted")||"#888";
    colGrid=col("--border")||"#ddd"; colAccent=col("--accent")||"#1f4e79";
    colGood=col("--good")||"#17784a"; colBg=col("--eq")||"#fff";
  }

  ctx.fillStyle=colBg; ctx.fillRect(0,0,W,H);

  const pasX=joliPas(xmax-xmin), pasY=joliPas(ymax-ymin);
  const axeX=(ymin<=0&&0<=ymax), axeY=(xmin<=0&&0<=xmax);
  const y0=axeX?Y(0):H-padB, x0=axeY?X(0):padL;

  // grille
  ctx.strokeStyle=colGrid; ctx.lineWidth=1;
  for(let x=Math.ceil(xmin/pasX)*pasX; x<=xmax+1e-9; x+=pasX){
    ctx.beginPath(); ctx.moveTo(X(x),padT); ctx.lineTo(X(x),H-padB); ctx.stroke();
  }
  for(let y=Math.ceil(ymin/pasY)*pasY; y<=ymax+1e-9; y+=pasY){
    ctx.beginPath(); ctx.moveTo(padL,Y(y)); ctx.lineTo(W-padR,Y(y)); ctx.stroke();
  }

  // axes avec flèches et libellés x/y
  ctx.strokeStyle=colFg; ctx.fillStyle=colFg; ctx.lineWidth=1.4;
  ctx.beginPath(); ctx.moveTo(padL,y0); ctx.lineTo(W-padR,y0); ctx.stroke();
  fleche(ctx, W-padR, y0, 0);
  ctx.font="italic 13px Georgia, serif"; ctx.fillText("x", W-padR-2, y0-9);
  ctx.beginPath(); ctx.moveTo(x0,H-padB); ctx.lineTo(x0,padT); ctx.stroke();
  fleche(ctx, x0, padT, -Math.PI/2);
  ctx.fillText("y", x0+9, padT+13);

  // graduations
  ctx.font="11px system-ui"; ctx.fillStyle=colMuted;
  for(let x=Math.ceil(xmin/pasX)*pasX; x<=xmax+1e-9; x+=pasX){
    if(Math.abs(x)<pasX*1e-6) continue;
    const px=X(x);
    ctx.strokeStyle=colFg; ctx.beginPath(); ctx.moveTo(px,y0-4); ctx.lineTo(px,y0+4); ctx.stroke();
    ctx.fillText(etiquette(x), px-6, y0+(y0<H/2?-8:16));
  }
  for(let y=Math.ceil(ymin/pasY)*pasY; y<=ymax+1e-9; y+=pasY){
    if(Math.abs(y)<pasY*1e-6) continue;
    const py=Y(y);
    ctx.strokeStyle=colFg; ctx.beginPath(); ctx.moveTo(x0-4,py); ctx.lineTo(x0+4,py); ctx.stroke();
    ctx.fillText(etiquette(y), x0+(x0<W/2?8:-24), py+4);
  }
  ctx.fillText("0", x0+(x0<W/2?6:-16), y0+(y0<H/2?-6:16));

  // asymptotes (pointillé)
  ctx.setLineDash([5,4]); ctx.strokeStyle=colAccent; ctx.lineWidth=1.2;
  (asymptotes||[]).forEach(a=>{
    if(a.genre==="horizontale" && a.valeur_val!=null){
      const y=Y(a.valeur_val); ctx.beginPath(); ctx.moveTo(padL,y); ctx.lineTo(W-padR,y); ctx.stroke();
    } else if(a.genre==="verticale" && a.point_val!=null){
      const x=X(a.point_val); ctx.beginPath(); ctx.moveTo(x,padT); ctx.lineTo(x,H-padB); ctx.stroke();
    } else if(a.genre==="oblique" && a.a_val!=null && a.b_val!=null){
      const y1=a.a_val*xmin+a.b_val, y2=a.a_val*xmax+a.b_val;
      ctx.beginPath(); ctx.moveTo(X(xmin),Y(y1)); ctx.lineTo(X(xmax),Y(y2)); ctx.stroke();
    }
  });
  ctx.setLineDash([]);

  // courbe — on ne lève le crayon qu'aux vrais trous (y=null, hors ED) ; sinon
  // on laisse le canevas découper proprement aux bords (comme ylim() en
  // matplotlib), en bornant juste les valeurs énormes (près d'une asymptote)
  // pour rester dans des coordonnées raisonnables.
  ctx.strokeStyle=colAccent; ctx.lineWidth=2.4; ctx.lineJoin="round"; ctx.lineCap="round";
  ctx.save();
  ctx.beginPath(); ctx.rect(padL,padT,availW,availH); ctx.clip();
  const borneY=y=>Math.max(ymin-50*(ymax-ymin), Math.min(ymax+50*(ymax-ymin), y));
  (g.segments||[]).forEach(seg=>{
    ctx.beginPath(); let dessine=false;
    seg.forEach(([x,y])=>{
      if(y==null){ dessine=false; return; }
      const px=X(x), py=Y(borneY(y));
      if(!dessine){ ctx.moveTo(px,py); dessine=true; } else { ctx.lineTo(px,py); }
    });
    ctx.stroke();
  });
  ctx.restore();

  // trous (limite finie en une valeur interdite) : rond vide
  (asymptotes||[]).forEach(a=>{
    if(a.genre!=="trou" || a.point_val==null || a.valeur_val==null) return;
    if(a.point_val<xmin||a.point_val>xmax||a.valeur_val<ymin||a.valeur_val>ymax) return;
    const px=X(a.point_val), py=Y(a.valeur_val);
    ctx.fillStyle=colBg; ctx.beginPath(); ctx.arc(px,py,4.5,0,2*Math.PI); ctx.fill();
    ctx.strokeStyle=colAccent; ctx.lineWidth=2; ctx.beginPath(); ctx.arc(px,py,4.5,0,2*Math.PI); ctx.stroke();
  });

  // extrema
  (extrema||[]).forEach(e=>{
    if(e.x_val==null || e.f_val==null) return;
    if(e.x_val<xmin||e.x_val>xmax||e.f_val<ymin||e.f_val>ymax) return;
    const px=X(e.x_val), py=Y(e.f_val);
    ctx.fillStyle=colBg; ctx.beginPath(); ctx.arc(px,py,4.5,0,2*Math.PI); ctx.fill();
    ctx.fillStyle=colGood; ctx.beginPath(); ctx.arc(px,py,3.5,0,2*Math.PI); ctx.fill();
    ctx.fillStyle=colFg; ctx.font="11px system-ui";
    ctx.fillText(`(${etiquette(e.x_val)} ; ${etiquette(e.f_val)})`, px+7, py-7);
  });
}


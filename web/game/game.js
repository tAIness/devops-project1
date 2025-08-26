// SPRITE_OK v1 (auto-start + bright palette + simple sprite animation)
(() => {
  const canvas = document.getElementById('game');
  const c = canvas.getContext('2d');

  // Bright palette
  const PAL = {
    sky: '#9ed8ff',
    hill: '#cfeafc',
    ground: '#b08a6a',
    platform: '#c8b07d',
    playerBody: '#1e88e5',  // overalls
    playerShirt: '#f44336', // shirt
    playerHat: '#d32f2f',
    skin: '#ffddb5',
    boots: '#3e2723',
    enemy: '#6d4c41',
    coin: '#ffd54a',
    coinStroke: '#916d12',
    hud: '#1e2430',
    stroke: 'rgba(0,0,0,0.35)',
    overlay: 'rgba(255,255,255,0.45)'
  };

  // World
  const GROUND_Y = canvas.height - 80;
  const GRAVITY = 0.9, FRICTION = 0.82, SPEED = 4.0, JUMP_VELOCITY = -16;

  // Entities
  const player = { x:80, y:GROUND_Y-44, w:36, h:44, vx:0, vy:0, onGround:true, alive:true, score:0 };
  const platforms = [
    { x:0,   y:GROUND_Y,       w:canvas.width, h:80 },   // ground
    { x:260, y:GROUND_Y-120,   w:120,          h:16 },
    { x:520, y:GROUND_Y-180,   w:140,          h:16 },
  ];
  const coins = [
    { x:300, y:GROUND_Y-160, r:10, taken:false },
    { x:560, y:GROUND_Y-220, r:10, taken:false },
    { x:740, y:GROUND_Y-90,  r:10, taken:false },
  ];
  const enemies = [
    { x:420, y:GROUND_Y-16, w:26, h:16, dir:-1, speed:1.2 },
    { x:680, y:GROUND_Y-16, w:26, h:16, dir: 1, speed:1.4 },
  ];

  // State
  let running = false;
  const keys = new Set();
  let animT = 0; // walk cycle timer

  // Controls
  function start(){ if(!running){ running = true; requestAnimationFrame(loop); } }
  function reset(full=true){
    Object.assign(player, { x:80, y:GROUND_Y-44, vx:0, vy:0, onGround:true, alive:true });
    if(full) player.score = 0;
    coins.forEach(c=>c.taken=false);
    draw();
  }

  // Input
  addEventListener('keydown', (e) => {
    keys.add(e.key);
    if ((e.key === ' ' || e.key === 'ArrowUp') && player.onGround && running) {
      player.vy = JUMP_VELOCITY; player.onGround = false; e.preventDefault();
    }
    if (!running && (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'Enter')) start();
  });
  addEventListener('keyup', (e) => keys.delete(e.key));
  addEventListener('click', () => start(), { once:true });
  canvas.addEventListener('click', () => start(), { once:true });

  window.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    if (startBtn) startBtn.onclick = start;
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) resetBtn.onclick = () => reset(true);
  });

  // --- Drawing helpers -------------------------------------------------------
  function drawBackground(){
    c.fillStyle = PAL.sky; c.fillRect(0,0,canvas.width,canvas.height);
    c.fillStyle = PAL.hill; c.fillRect(0,GROUND_Y-60,canvas.width,60);
    const g = platforms[0];
    c.fillStyle = PAL.ground; c.fillRect(g.x,g.y,g.w,g.h);
    c.strokeStyle = PAL.stroke; c.lineWidth = 2; c.strokeRect(g.x,g.y,g.w,g.h);
    for (const p of platforms.slice(1)) {
      c.fillStyle = PAL.platform; c.fillRect(p.x,p.y,p.w,p.h);
      c.strokeStyle = PAL.stroke; c.lineWidth = 2; c.strokeRect(p.x,p.y,p.w,p.h);
    }
  }

  function drawCoins(){
    for (const co of coins) {
      if (co.taken) continue;
      c.fillStyle = PAL.coin;
      c.beginPath(); c.arc(co.x,co.y,co.r,0,Math.PI*2); c.fill();
      c.strokeStyle = PAL.coinStroke; c.lineWidth = 3; c.stroke();
    }
  }

  function drawEnemies(){
    c.fillStyle = PAL.enemy;
    for (const e of enemies) {
      c.fillRect(e.x,e.y,e.w,e.h);
      c.strokeStyle = PAL.stroke; c.lineWidth = 2; c.strokeRect(e.x,e.y,e.w,e.h);
    }
  }

  function drawHUD(){
    c.fillStyle = PAL.hud;
    c.font = '16px system-ui, sans-serif';
    c.fillText(`Score: ${player.score}`, 16, 24);
    if (!running) {
      c.fillStyle = PAL.overlay; c.fillRect(0,0,canvas.width,canvas.height);
      c.fillStyle = PAL.hud; c.font = 'bold 24px system-ui, sans-serif';
      c.fillText('Press Start to play', canvas.width/2 - 110, canvas.height/2);
    }
    if (!player.alive) {
      c.fillStyle = PAL.overlay; c.fillRect(0,0,canvas.width,canvas.height);
      c.fillStyle = PAL.hud; c.font = 'bold 28px system-ui, sans-serif';
      c.fillText('Game Over', canvas.width/2 - 70, canvas.height/2 - 10);
      c.font = '16px system-ui, sans-serif';
      c.fillText('Click Reset to try again', canvas.width/2 - 98, canvas.height/2 + 18);
    }
  }

  // Simple original "plumber" sprite (not Nintendo IP)
  function drawPlumber(x, y, w, h, vx, onGround) {
    const dir = vx >= 0 ? 1 : -1;
    const cx = x + w/2, cy = y + h/2;

    // Walk cycle (legs swing)
    const speed = Math.min(Math.abs(vx) / SPEED, 1);
    animT += 0.15 * (speed + 0.2); // idle still animates a bit
    const swing = Math.sin(animT) * 4 * (onGround ? 1 : 0.3);

    c.save();
    c.translate(cx, y);

    // LEGS
    c.fillStyle = PAL.playerBody;
    c.strokeStyle = PAL.stroke; c.lineWidth = 2;
    // left leg
    c.save(); c.translate(-8, 26 + swing); c.fillRect(-6, 0, 10, 12); c.strokeRect(-6, 0, 10, 12);
    c.fillStyle = PAL.boots; c.fillRect(-8, 10, 14, 6); c.restore();
    // right leg
    c.fillStyle = PAL.playerBody;
    c.save(); c.translate(8, 26 - swing); c.fillRect(-4, 0, 10, 12); c.strokeRect(-4, 0, 10, 12);
    c.fillStyle = PAL.boots; c.fillRect(-6, 10, 14, 6); c.restore();

    // TORSO (overalls)
    c.fillStyle = PAL.playerBody;
    c.fillRect(-14, 10, 28, 22); c.strokeRect(-14, 10, 28, 22);
    // Shirt sleeves
    c.fillStyle = PAL.playerShirt;
    c.fillRect(-20, 12, 6, 10); c.fillRect(14, 12, 6, 10);
    // Straps
    c.fillStyle = '#0d47a1';
    c.fillRect(-10, 10, 6, 14); c.fillRect(4, 10, 6, 14);

    // ARMS
    c.fillStyle = PAL.playerShirt;
    // left arm
    c.save(); c.translate(-22*dir, 14); c.scale(dir, 1); c.fillRect(-6, 0, 12, 8); c.restore();
    // right arm
    c.save(); c.translate(22*dir, 14); c.scale(dir, 1); c.fillRect(-6, 0, 12, 8); c.restore();

    // HEAD
    // neck
    c.fillStyle = PAL.skin; c.fillRect(-4, 6, 8, 6);
    // head circle
    c.beginPath(); c.arc(0, 6, 9, 0, Math.PI*2); c.fillStyle = PAL.skin; c.fill();
    c.strokeStyle = PAL.stroke; c.stroke();
    // hat
    c.fillStyle = PAL.playerHat;
    c.fillRect(-10, -2, 20, 8);
    c.fillRect(dir>0 ? -10 : -8, 4, dir>0 ? 14 : 18, 3); // brim
    // eyes
    c.fillStyle = '#111';
    c.fillRect(-3 + 2*dir, 4, 3, 3); c.fillRect(2 + 2*dir, 4, 3, 3);
    // mustache
    c.fillStyle = '#3a2a20'; c.fillRect(-6, 8, 12, 2);

    c.restore();
  }

  // --- Physics ----------------------------------------------------------------
  function rectIntersect(a,b){ return a.x<b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y; }

  function physics(){
    if (keys.has('ArrowLeft')) player.vx = -SPEED;
    else if (keys.has('ArrowRight')) player.vx = SPEED;
    else player.vx *= FRICTION;

    player.x += player.vx;
    player.vy += GRAVITY; player.y += player.vy;

    player.onGround = false;
    for (const p of platforms) {
      if (player.y + player.h > p.y && player.y + player.h < p.y + p.h &&
          player.x + player.w > p.x && player.x < p.x + p.w && player.vy >= 0) {
        player.y = p.y - player.h; player.vy = 0; player.onGround = true;
      }
    }

    if (player.x < 0) player.x = 0;
    if (player.x + player.w > canvas.width) player.x = canvas.width - player.w;
    if (player.y + player.h > canvas.height) { player.y = canvas.height - player.h; player.vy = 0; player.onGround = true; }

    for (const e of enemies) {
      e.x += e.dir * e.speed * 2.4;
      if (e.x < 360) { e.x = 360; e.dir *= -1; }
      if (e.x + e.w > canvas.width - 40) { e.x = canvas.width - 40 - e.w; e.dir *= -1; }
      if (rectIntersect(player, e) && player.alive) {
        if (player.vy > 0 && player.y + player.h - e.y < 18) {
          player.vy = JUMP_VELOCITY * 0.6; player.score += 100; e.x = 480;
        } else {
          player.alive = false; running = false;
        }
      }
    }

    for (const co of coins) {
      if (co.taken) continue;
      const dx = (player.x + player.w/2) - co.x;
      const dy = (player.y + player.h/2) - co.y;
      if (Math.hypot(dx, dy) < co.r + Math.max(player.w, player.h)/2 - 10) {
        co.taken = true; player.score += 50;
      }
    }
  }

  // --- Main loop --------------------------------------------------------------
  function loop(){ if(!running){ draw(); return; } physics(); draw(); requestAnimationFrame(loop); }
  function draw(){ drawBackground(); drawCoins(); drawEnemies(); drawPlumber(player.x,player.y,player.w,player.h,player.vx,player.onGround); drawHUD(); }

  reset(true);
})();

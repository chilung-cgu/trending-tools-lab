import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'artifacts/cad');
const assets = path.join(output, 'assets');
fs.mkdirSync(assets, { recursive: true });
for (const file of ['build/three.module.js', 'build/three.core.js', 'examples/jsm/controls/OrbitControls.js', 'examples/jsm/loaders/GLTFLoader.js', 'examples/jsm/utils/BufferGeometryUtils.js', 'examples/jsm/utils/SkeletonUtils.js', 'LICENSE']) {
  const target = path.join(assets, file);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(path.join(root, 'node_modules/three', file), target);
}
const geometry = JSON.parse(fs.readFileSync(path.join(output, 'geometry.json')));
const dims = geometry.dimensions_mm;
const document = `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>三槽理線器 · 3D 實驗室</title>
<style>*{box-sizing:border-box}body{margin:0;background:#eef3f5;color:#18333e;font-family:system-ui,sans-serif;line-height:1.7}main{max-width:1100px;margin:auto;padding:28px 20px}a{color:#145943;text-underline-offset:4px}#viewer{width:100%;height:clamp(320px,65vh,650px);background:#e6edf1;border-radius:12px;overflow:hidden}canvas{display:block;touch-action:none}button{font:inherit;padding:8px 16px;border:1px solid #94aca1;background:white;border-radius:8px;cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid #145943;outline-offset:3px}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:18px 0}h1{margin-bottom:8px}p{margin-top:8px}</style>
<script type="importmap">{"imports":{"three":"./assets/build/three.module.js","three/addons/":"./assets/examples/jsm/"}}</script></head><body><main>
<a href="../../index.html">← 回到成品入口</a><h1>三槽桌面理線器</h1><p><span>${dims.width} × ${dims.depth} × ${dims.height} mm</span> · ${geometry.solid_count} 個實體 · 體積 ${geometry.volume_mm3.toLocaleString('en-US')} mm³</p>
<p>拖曳旋轉，滾輪／雙指縮放，右鍵拖曳平移。模型來自實際 CAD 匯出的 GLB。</p><div id="viewer" aria-label="理線器三維模型"></div>
<div class="controls"><button id="reset">重設視角</button><label><input type="checkbox" id="wireframe"> 顯示網格線</label><span role="status">正在載入 3D 模型…</span></div>
<p><a href="cable_organizer.step" download>下載 STEP</a> · <a href="cable_organizer.stl" download>下載 STL</a> · <a href="cable_organizer.glb" download>下載 GLB</a> · <a href="cable_organizer_drawing.pdf">查看工程圖 PDF</a> · <a href="../../docs/text-to-cad.html">改尺寸與玩法</a></p>
<p>此為幾何示範；線材卡入能力、材料彈性及製造公差尚未實測。</p>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const host=document.getElementById('viewer'), status=document.querySelector('[role=status]');
try {
 const scene=new THREE.Scene(); scene.background=new THREE.Color('#e6edf1');
 const camera=new THREE.PerspectiveCamera(38,host.clientWidth/host.clientHeight,0.1,10000);
 const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(host.clientWidth,host.clientHeight); host.append(renderer.domElement);
 scene.add(new THREE.HemisphereLight(0xffffff,0x586470,3));
 const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(60,-100,150);scene.add(light);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
 let meshes=[];
 new GLTFLoader().load('./cable_organizer.glb',gltf=>{
  scene.add(gltf.scene);
  const box=new THREE.Box3().setFromObject(gltf.scene), center=box.getCenter(new THREE.Vector3()), size=box.getSize(new THREE.Vector3()), extent=Math.max(size.x,size.y,size.z);
  controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(extent*1.2,extent*1.1,extent*1.5));camera.near=extent/1000;camera.far=extent*100;camera.updateProjectionMatrix();controls.update();controls.saveState();
  gltf.scene.traverse(o=>{if(o.isMesh){o.material=new THREE.MeshStandardMaterial({color:'#69918c',roughness:0.6,metalness:0.05});meshes.push(o);}});
  window.labViewer={camera,controls};status.textContent='3D 模型已載入';
 },undefined,()=>{status.textContent='模型載入失敗；請從專案根目錄啟動 HTTP 伺服器，或下载 STEP。';});
 document.getElementById('reset').addEventListener('click',()=>controls.reset());
 document.getElementById('wireframe').addEventListener('change',e=>meshes.forEach(mesh=>mesh.material.wireframe=e.target.checked));
 const observer=new ResizeObserver(()=>{camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();renderer.setSize(host.clientWidth,host.clientHeight);});observer.observe(host);
 renderer.setAnimationLoop(()=>renderer.render(scene,camera));
}catch(error){status.textContent='此瀏覽器無法啟用 WebGL；仍可下載 STEP/STL 或查看 PDF 工程圖。';}
</script></main></body></html>`;
fs.writeFileSync(path.join(output, 'index.html'), document);
console.log('Built portable CAD viewer with local Three.js assets.');

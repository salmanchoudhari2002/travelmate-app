const map = L.map('map').setView([20,0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

const resultsDiv = document.getElementById('results');
const detailDiv = document.getElementById('place-detail');
let markers = [];

function clearMarkers(){
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}

function showPlace(p){
  detailDiv.innerHTML = '';
  const title = document.createElement('h4');
  title.textContent = p.name || p.display_name;
  detailDiv.appendChild(title);
  if (p.icon){
    const img = document.createElement('img');
    img.src = p.icon;
    img.style.maxWidth = '100%';
    detailDiv.appendChild(img);
  }
  const link = document.createElement('a');
  link.href = p.osm_url || '#';
  link.textContent = 'Open in OSM';
  link.target = '_blank';
  detailDiv.appendChild(link);
}

document.getElementById('search').addEventListener('click', async ()=>{
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  resultsDiv.innerHTML = 'Searching...';
  const res = await fetch(`/map/search?query=${encodeURIComponent(q)}&limit=10`);
  const data = await res.json();
  resultsDiv.innerHTML = '';
  clearMarkers();
  data.results.forEach((r, idx)=>{
    const el = document.createElement('div');
    el.className = 'result';
    el.textContent = r.name || r.display_name;
    el.onclick = ()=>{
      showPlace(r);
      map.setView([r.lat, r.lon], 15);
    };
    resultsDiv.appendChild(el);
    if (r.lat && r.lon){
      const m = L.marker([r.lat, r.lon]);
      m.addTo(map).bindPopup(r.name || r.display_name);
      markers.push(m);
    }
  });
});

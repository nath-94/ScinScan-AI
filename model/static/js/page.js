const openCameraBtn = document.getElementById('open-camera-btn');
const cameraModal = document.getElementById('camera-modal');
const video = document.getElementById('video');
const takePhotoBtn = document.getElementById('take-photo-btn');
const closeCameraBtn = document.getElementById('close-camera-btn');
const canvas = document.getElementById('canvas');
const fileInput = document.getElementById('file-input');
const previewImage = document.getElementById('preview-image');

let stream = null;

if (openCameraBtn) {
  openCameraBtn.onclick = async function() {
    cameraModal.style.display = 'flex';
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
  };
}

if (closeCameraBtn) {
  closeCameraBtn.onclick = function() {
    cameraModal.style.display = 'none';
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };
}

if (takePhotoBtn) {
  takePhotoBtn.onclick = function() {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(function(blob) {

        const file = new File([blob], "photo.jpg", {type: "image/jpeg"});
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;

      const url = URL.createObjectURL(blob);
      if (previewImage) previewImage.src = url;

      cameraModal.style.display = 'none';
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      fileInput.dispatchEvent(new Event('change'));
    }, 'image/jpeg');
  };
}

const map = L.map('map').setView([46.5, 2.5], 6);

  // Fond de carte
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  // Charger ton GeoJSON
  fetch("{{ url_for('static', filename='data/annuaire.geojson') }}")
    .then(res => res.json())
    .then(data => {
      L.geoJSON(data, {
        onEachFeature: (feature, layer) => {
          const props = feature.properties;
          const nom = props["nom"] || "Inconnu";
          const adresse = props["adresse"] || "";
          const ville = props["dep_name"] || "";
          const cp = props["Code code_commune"] || "";
          layer.bindPopup(`<strong>${nom}</strong><br>${adresse}<br>${cp} ${ville}`);
        }
      }).addTo(map);
    });

  // Géocodage avec Nominatim
  async function geocode(city) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(city)}`;
    const [res] = await fetch(url, { headers:{'User-Agent':'derm-app'} }).then(r => r.json());
    if (!res) throw "Ville introuvable";
    return { lat: parseFloat(res.lat), lon: parseFloat(res.lon) };
  }

  document.getElementById('goBtn').addEventListener('click', async () => {
    const city = document.getElementById('cityInput').value.trim();
    if (!city) return;
    try {
      const coords = await geocode(city);
      map.setView([coords.lat, coords.lon], 13);
    } catch (e) {
      alert(e);
    }
  });
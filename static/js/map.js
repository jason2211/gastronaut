'use strict';

let mapOpen = true;
let mappyBoi;
let userMarker;
let restMarker;
const markerOptions = { color: '#3bdb53' };
const fitBoundsOptions = [
  {
    padding: { top: 80, bottom: 10, left: 80, right: 80 },
  },
  {
    padding: { top: 80, bottom: 40, left: 200, right: 200 },
  },
];

function renderMiniMap(mapCenter = [-85, 26.8], zoom = 1.3) {
  mapboxgl.accessToken =
    'pk.eyJ1Ijoia29ua3JlciIsImEiOiJja2NiNnI3bjgyMjVnMnJvNmJ6dTF0enlmIn0.AH_5N70IYIX4_tslm49Kmw';
  var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/konkrer/ckbslmn3x00y31hp7vh351zxb/draft', // <<<<< remove /draft in production
    center: mapCenter,
    pitch: 34,
    zoom,
  });
  map.addControl(new mapboxgl.FullscreenControl());
  // map.addControl(new mapboxgl.NavigationControl());

  return map;
}

function addUserMarker(coords) {
  userMarker = new mapboxgl.Marker(markerOptions)
    .setLngLat(coords)
    .setPopup(new mapboxgl.Popup().setHTML(`<b><em>You</em></b>`))
    .addTo(mappyBoi);
  // userMarker.togglePopup();
  return userMarker;
}

function fitBounds(userCoords, restCoords, name) {
  if (restMarker) restMarker.remove();
  let optIdx = isMobileScreen() ? 0 : 1;
  mappyBoi.fitBounds([userCoords, restCoords], fitBoundsOptions[optIdx]);
  restMarker = new mapboxgl.Marker(markerOptions)
    .setLngLat(restCoords)
    .setPopup(new mapboxgl.Popup().setHTML(`<b><em>${name}</em></b>`))
    .addTo(mappyBoi);
  restMarker.togglePopup();
}

// check if screen size is mobile.
function isMobileScreen() {
  if (window.innerWidth <= 880) return true;
  return false;
}

// check if screen size is mobile.
function isMobilePortrait() {
  if (window.innerWidth <= 450) return true;
  return false;
}

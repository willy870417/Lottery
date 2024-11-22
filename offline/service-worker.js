const CACHE_NAME = 'lottery-cache-v3';
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/button.jpg',
    '/service-worker.js',
    'https://cdn.tailwindcss.com'  // TailwindCSS CDN
    // 加上所有必要的 CSS、JS 和圖片資源
];

// 安裝 Service Worker 並緩存資源
self.addEventListener('install', function(event) {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function(cache) {
          console.log('Opened cache');
          return cache.addAll(urlsToCache);
        })
    );
  });
  
  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request)
        .then(function(response) {
          // 如果找到匹配的緩存，則返回
          if (response) {
            return response;
          }
          // 否則，從網絡請求並緩存該資源
          return fetch(event.request).then(function(networkResponse) {
            if (!networkResponse || networkResponse.status !== 200) {
              return networkResponse;
            }
            return caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, networkResponse.clone());
              return networkResponse;
            });
          }).catch(function() {
            // 返回離線頁面或占位符
            return caches.match('/offline.html');
          });
        })
    );
  });
  
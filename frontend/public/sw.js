// frontend/public/sw.js

// Service Worker for Push Notifications

self.addEventListener('install', event => {
    console.log('Service Worker installing.');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Service Worker activating.');
    event.waitUntil(clients.claim());
});

self.addEventListener('push', event => {
    console.log('Push message received:', event);

    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const options = {
        body: data.body || 'You have a new notification',
        icon: '/favicon.png',
        badge: '/favicon.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: data.primaryKey || 1
        },
        actions: [
            {
                action: 'view',
                title: 'View Details'
            },
            {
                action: 'dismiss',
                title: 'Dismiss'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'Gabani Transport Solutions (GTS)', options)
    );
});

self.addEventListener('notificationclick', event => {
    console.log('Notification click received:', event);

    event.notification.close();

    if (event.action === 'view') {
        // Open the app and navigate to relevant page
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

self.addEventListener('notificationclose', event => {
    console.log('Notification closed:', event);
});

// Background sync for offline notifications
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    console.log('Background sync triggered');
    // Implement background sync logic here
    // This could check for pending notifications or updates
}

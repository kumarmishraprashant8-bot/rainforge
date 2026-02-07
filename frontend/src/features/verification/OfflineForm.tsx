import { useState, useEffect } from 'react';

export default function OfflineForm() {
    const [projectId, setProjectId] = useState('');
    const [photo, setPhoto] = useState<File | null>(null);
    const [status, setStatus] = useState<string>('idle'); // idle, saved, syncing
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    useEffect(() => {
        const handleStatusChange = () => setIsOnline(navigator.onLine);
        window.addEventListener('online', handleStatusChange);
        window.addEventListener('offline', handleStatusChange);
        return () => {
            window.removeEventListener('online', handleStatusChange);
            window.removeEventListener('offline', handleStatusChange);
        };
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!photo || !projectId) return;

        const verificationData = {
            id: Date.now(),
            project_id: projectId,
            timestamp: new Date().toISOString(),
            // In a real app we'd convert photo to blob/base64 to store in simple IndexedDB
            // or keep it as File object if IDB Wrapper supports it (it usually does)
            status: 'pending'
        };

        if ('serviceWorker' in navigator && 'SyncManager' in window) {
            try {
                const swReg = await navigator.serviceWorker.ready;

                // Write to IndexedDB (Helper function assumed available or inline)
                const db = await openDB();
                const tx = db.transaction('verification-queue', 'readwrite');
                tx.objectStore('verification-queue').add(verificationData);
                tx.oncomplete = () => console.log('Transaction complete');

                // Register Sync
                await (swReg as any).sync.register('sync-verifications');
                setStatus('saved');
                alert('Verification saved! It will sync automatically when online.');
            } catch (err) {
                console.error('Background Sync failed', err);
                setStatus('error');
            }
        } else {
            // Fallback for browsers without SyncManager
            alert('Your browser does not support background sync.');
        }
    };

    // Simple IDB helper embedded for the component logic visualization
    const openDB = () => {
        return new Promise<IDBDatabase>((resolve, reject) => {
            const request = indexedDB.open('rainforge-offline', 1);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    return (
        <div className="p-4 bg-white rounded shadow dark:bg-slate-800">
            <h2 className="text-xl font-bold mb-4">Offline Verification</h2>
            <div className={`mb-4 text-sm ${isOnline ? 'text-green-500' : 'text-amber-500'}`}>
                Status: {isOnline ? 'Online' : 'Offline (Background Sync Ready)'}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium">Project ID</label>
                    <input
                        type="text"
                        value={projectId}
                        onChange={e => setProjectId(e.target.value)}
                        className="w-full p-2 border rounded dark:bg-slate-700"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium">Photo Proof</label>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={e => setPhoto(e.target.files?.[0] || null)}
                        className="w-full p-2 border rounded dark:bg-slate-700"
                        required
                    />
                </div>

                <button
                    type="submit"
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full"
                >
                    Submit Verification
                </button>
            </form>
        </div>
    );
}


import api from '@/api'

// Config
const CHUNK_SIZE = 20 * 1024 * 1024; // 20MB - Balanced for CF Tunnel
const MAX_RETRIES = 3;
const THRESHOLD_SIZE = 50 * 1024 * 1024; // 50MB

/**
 * Uploads a file, automatically using chunked upload if large.
 * @param {File} file 
 * @param {Object} options { onProgress, settings (password, expire, etc), uploadMode }
 * @returns {Promise<Object>} The uploaded file object
 */
export async function smartUpload(file, options = {}) {
    // Check if we should use chunked upload
    if (file.size > THRESHOLD_SIZE) {
        return uploadChunked(file, options);
    } else {
        // Normal upload handled by caller or we can standardize here?
        // For now, let's assume this utility handles both or just chunked.
        // The caller currently handles normal. So this helper is specifically for large files 
        // or we wrap everything.
        // Let's implement chunked logic here.
        return uploadChunked(file, options); // Force chunked for testing or strictly > threshold
    }
}

/**
 * Core chunked upload logic
 */
export async function uploadChunked(file, { onProgress, settings = {}, uploadMode = 'file' } = {}) {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    let uploadId = null;

    try {
        // 1. Init
        const initRes = await api.post('/chunk/init', {
            filename: file.name,
            file_size: file.size,
            mime_type: file.type || 'application/octet-stream',
            total_chunks: totalChunks,
            upload_mode: uploadMode
        });

        uploadId = initRes.data.upload_id;
        const serverChunkSize = initRes.data.chunk_size || CHUNK_SIZE;

        // 2. Check resume status (Optional, good for refresh)
        // For now, we assume fresh start or robust retry
        // const statusRes = await api.get(`/chunk/status/${uploadId}`);
        // const uploadedChunks = new Set(statusRes.data.uploaded_chunks);
        const uploadedChunks = new Set();

        // 3. Upload Chunks
        for (let i = 0; i < totalChunks; i++) {
            if (uploadedChunks.has(i)) {
                // Update progress
                const progress = Math.round(((i + 1) / totalChunks) * 100);
                if (onProgress) onProgress(progress);
                continue;
            }

            const start = i * serverChunkSize;
            const end = Math.min(start + serverChunkSize, file.size);
            const chunk = file.slice(start, end);

            // Upload with retry
            let retries = 0;
            while (true) {
                try {
                    const formData = new FormData();
                    formData.append('chunk_index', i);
                    formData.append('file', chunk, `part_${i}`);

                    await api.post(`/chunk/upload/${uploadId}`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' },
                        // timeout?
                    });
                    break; // Success
                } catch (e) {
                    retries++;
                    if (retries > MAX_RETRIES) throw e;
                    // Wait small delay
                    await new Promise(r => setTimeout(r, 1000 * retries));
                }
            }

            // Progress
            const progress = Math.round(((i + 1) / totalChunks) * 100);
            if (onProgress) onProgress(progress);
        }

        // 4. Complete
        const completePayload = {
            upload_id: uploadId,
            password: settings.password,
            download_limit: settings.downloadLimit ? Number(settings.downloadLimit) : null,
            expire_days: settings.expireDays
        };

        const completeRes = await api.post(`/chunk/complete/${uploadId}`, completePayload);
        return completeRes.data;

    } catch (e) {
        console.error("Chunk upload failed", e);
        throw e;
    }
}

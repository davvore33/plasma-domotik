import { TradfriClient } from 'node-tradfri-client';
import http from 'http';
import fs from 'fs';
import path from 'path';
import os from 'os';

const CONFIG_FILE = path.join(process.env.HOME, '.config/plasma-domotik/tradfri_psk.json');
const PORT = 8765;

let tradfri = null;
let connected = false;
let devicesCache = new Map();
let observeActive = false;
let initialDiscoveryDone = false;
let initialDiscoveryResolve = null;

function loadConfig() {
    try {
        const conf = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
        for (const [host, creds] of Object.entries(conf)) {
            return { host, identity: creds.identity, psk: creds.key };
        }
    } catch (e) {
        console.error('Config load error:', e.message);
    }
    return null;
}

function mapDevice(device) {
    const isLight = device.lightList && device.lightList.length > 0;
    const isPlug = device.plugList && device.plugList.length > 0;
    const isBlind = device.blindList && device.blindList.length > 0;
    
    let type = 'unknown';
    if (isLight) type = 'light';
    else if (isPlug) type = 'plug';
    else if (isBlind) type = 'blind';
    
    const capabilities = [];
    if (isLight) {
        capabilities.push('on_off');
        const light = device.lightList[0];
        if (light.isDimmable) capabilities.push('brightness');
        if (light.colorX !== undefined || light.colorY !== undefined) capabilities.push('color');
        if (light.colorTemperature !== undefined) capabilities.push('color_temp');
    }
    if (isPlug) capabilities.push('on_off');
    if (isBlind) capabilities.push('position');
    
    const state = {};
    if (isLight) {
        const light = device.lightList[0];
        state.on = light.onOff;
        if (light.dimmer !== undefined) state.brightness = Math.round(light.dimmer / 254 * 100);
        if (light.color) state.color = light.color;
        if (light.colorTemperature !== undefined) state.color_temp = light.colorTemperature;
    }
    if (isPlug) {
        state.on = device.plugList[0].onOff;
    }
    
    return {
        id: String(device.instanceId),
        name: device.name || 'Unknown',
        type,
        reachable: device.alive || false,
        state,
        capabilities
    };
}

async function ensureConnected(overrideHost = null, overrideIdentity = null, overridePsk = null) {
    if (connected && tradfri) return true;
    
    let config = null;
    if (overrideHost && overrideIdentity && overridePsk) {
        config = { host: overrideHost, identity: overrideIdentity, psk: overridePsk };
    } else {
        config = loadConfig();
    }
    if (!config) return false;
    
    tradfri = new TradfriClient(config.host);
    tradfri.on('error', (err) => {
        console.error('Tradfri error:', err.message);
    });
    
    tradfri.on('device updated', (device) => {
        console.log('Device updated:', device.name, device.instanceId);
        devicesCache.set(String(device.instanceId), device);
    });
    
    tradfri.on('device removed', (deviceId) => {
        console.log('Device removed:', deviceId);
        devicesCache.delete(String(deviceId));
    });
    
    try {
        connected = await tradfri.connect(config.identity, config.psk);
        if (connected && !observeActive) {
            observeActive = true;
            tradfri.observeDevices();
            console.log('Device observation started');
        }
        return connected;
    } catch (e) {
        console.error('Connection failed:', e.message);
        connected = false;
        return false;
    }
}

async function connectWithSecurityCode(host, securityCode) {
    if (connected && tradfri) return { connected: true };
    
    try {
        tradfri = new TradfriClient(host);
        tradfri.on('error', (err) => {
            console.error('Tradfri error:', err.message);
        });
        tradfri.on('device updated', (device) => {
            console.log('Device updated:', device.name, device.instanceId);
            devicesCache.set(String(device.instanceId), device);
        });
        tradfri.on('device removed', (deviceId) => {
            console.log('Device removed:', deviceId);
            devicesCache.delete(String(deviceId));
        });
        
        const { identity, psk } = await tradfri.authenticate(securityCode);
        console.log('Authenticated with identity:', identity);
        
        // Save credentials
        fs.mkdirSync(path.dirname(CONFIG_FILE), { recursive: true });
        let conf = {};
        try {
            conf = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
        } catch (e) {}
        conf[host] = { identity, key: psk };
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(conf, null, 4));
        
        // Reconnect with the new credentials
        await tradfri.destroy();
        tradfri = new TradfriClient(host);
        tradfri.on('error', (err) => {
            console.error('Tradfri error:', err.message);
        });
        tradfri.on('device updated', (device) => {
            console.log('Device updated:', device.name, device.instanceId);
            devicesCache.set(String(device.instanceId), device);
        });
        tradfri.on('device removed', (deviceId) => {
            console.log('Device removed:', deviceId);
            devicesCache.delete(String(deviceId));
        });
        
        const reconnected = await tradfri.connect(identity, psk);
        if (!reconnected) {
            console.error('Failed to reconnect with new credentials');
            connected = false;
            return { connected: false, error: 'Failed to reconnect' };
        }
        
        connected = true;
        observeActive = true;
        tradfri.observeDevices();
        console.log('Device observation started');
        
        return { connected: true, identity, psk };
    } catch (e) {
        console.error('Authentication failed:', e.message);
        connected = false;
        return { connected: false, error: e.message };
    }
}

function getCachedDevices() {
    return Array.from(devicesCache.values()).map(mapDevice);
}

async function waitForInitialDiscovery(timeout = 10000) {
    if (devicesCache.size > 0) return;
    return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
            if (devicesCache.size > 0) {
                clearInterval(checkInterval);
                resolve();
            }
        }, 500);
        setTimeout(() => {
            clearInterval(checkInterval);
            resolve();
        }, timeout);
    });
}

const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    
    try {
        const url = new URL(req.url, `http://localhost:${PORT}`);
        
        switch (url.pathname) {
            case '/connect': {
                const host = url.searchParams.get('host');
                const identity = url.searchParams.get('identity');
                const psk = url.searchParams.get('psk');
                const securityCode = url.searchParams.get('securityCode');
                
                if (securityCode && host) {
                    const result = await connectWithSecurityCode(host, securityCode);
                    res.writeHead(200);
                    res.end(JSON.stringify(result));
                } else if (host && identity && psk) {
                    const ok = await ensureConnected(host, identity, psk);
                    res.writeHead(200);
                    res.end(JSON.stringify({ connected: ok }));
                } else {
                    const ok = await ensureConnected();
                    res.writeHead(200);
                    res.end(JSON.stringify({ connected: ok }));
                }
                break;
            }
            
            case '/devices': {
                if (!await ensureConnected()) {
                    res.writeHead(503);
                    res.end(JSON.stringify({ error: 'Not connected' }));
                    return;
                }
                
                await waitForInitialDiscovery();
                const devices = getCachedDevices();
                res.writeHead(200);
                res.end(JSON.stringify(devices));
                break;
            }
            
            case '/device': {
                const deviceId = url.searchParams.get('id');
                if (!deviceId) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Missing id parameter' }));
                    return;
                }
                
                if (!await ensureConnected()) {
                    res.writeHead(503);
                    res.end(JSON.stringify({ error: 'Not connected' }));
                    return;
                }
                
                let attempts = 0;
                while (!devicesCache.has(deviceId) && attempts < 20) {
                    await new Promise(r => setTimeout(r, 500));
                    attempts++;
                }
                
                const device = devicesCache.get(deviceId);
                if (!device) {
                    res.writeHead(404);
                    res.end(JSON.stringify({ error: 'Device not found' }));
                    return;
                }
                
                res.writeHead(200);
                res.end(JSON.stringify(mapDevice(device)));
                break;
            }
            
            case '/power': {
                const deviceId = url.searchParams.get('id');
                const state = url.searchParams.get('state') === 'true';
                
                if (!deviceId) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Missing id parameter' }));
                    return;
                }
                
                if (!await ensureConnected()) {
                    res.writeHead(503);
                    res.end(JSON.stringify({ error: 'Not connected' }));
                    return;
                }
                
                const device = devicesCache.get(deviceId);
                if (!device) {
                    res.writeHead(404);
                    res.end(JSON.stringify({ error: 'Device not found' }));
                    return;
                }
                
                try {
                    if (device.lightList && device.lightList.length > 0) {
                        device.lightList[0].onOff = state;
                        await tradfri.operateLight(device, { onOff: state });
                    } else if (device.plugList && device.plugList.length > 0) {
                        device.plugList[0].onOff = state;
                        await tradfri.operatePlug(device, { onOff: state });
                    } else {
                        res.writeHead(400);
                        res.end(JSON.stringify({ error: 'Device type not supported for power control' }));
                        return;
                    }
                    res.writeHead(200);
                    res.end(JSON.stringify({ success: true }));
                } catch (e) {
                    res.writeHead(500);
                    res.end(JSON.stringify({ success: false, error: e.message }));
                }
                break;
            }
            
            case '/brightness': {
                const deviceId = url.searchParams.get('id');
                const value = parseInt(url.searchParams.get('value'));
                
                if (!deviceId || isNaN(value)) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Missing id or value parameter' }));
                    return;
                }
                
                if (!await ensureConnected()) {
                    res.writeHead(503);
                    res.end(JSON.stringify({ error: 'Not connected' }));
                    return;
                }
                
                const device = devicesCache.get(deviceId);
                if (!device) {
                    res.writeHead(404);
                    res.end(JSON.stringify({ error: 'Device not found' }));
                    return;
                }
                
                try {
                    const dimmerValue = Math.round(Math.max(0, Math.min(100, value)) * 254 / 100);
                    await tradfri.operateLight(device, { dimmer: dimmerValue });
                    res.writeHead(200);
                    res.end(JSON.stringify({ success: true }));
                } catch (e) {
                    res.writeHead(500);
                    res.end(JSON.stringify({ success: false, error: e.message }));
                }
                break;
            }
            
            case '/disconnect': {
                if (tradfri) {
                    observeActive = false;
                    initialDiscoveryDone = false;
                    await tradfri.destroy();
                    tradfri = null;
                    connected = false;
                    devicesCache.clear();
                }
                res.writeHead(200);
                res.end(JSON.stringify({ disconnected: true }));
                break;
            }
            
            default: {
                res.writeHead(404);
                res.end(JSON.stringify({ error: 'Not found' }));
            }
        }
    } catch (e) {
        console.error('Server error:', e);
        res.writeHead(500);
        res.end(JSON.stringify({ error: e.message }));
    }
});

server.listen(PORT, '127.0.0.1', () => {
    console.log(`Tradfri Node Adapter listening on http://127.0.0.1:${PORT}`);
});

process.on('SIGINT', async () => {
    if (tradfri) await tradfri.destroy();
    server.close();
    process.exit(0);
});

const audio = document.getElementById("audio");
const volume = document.getElementById("volume");
const status = document.getElementById("status");

const roomId = window.location.pathname.split("/").filter(Boolean).pop();


let peerConnection = null;
let serverPosition = 0;
let lastAllowedPosition = 0;


// Initial audio settings

audio.volume = 1.0;
audio.playbackRate = 1.0;
audio.defaultPlaybackRate = 1.0;


// Local volume

volume.addEventListener("input", () => {
    const value = Number(volume.value);

    if (Number.isFinite(value) && value >= 0 && value <= 1) {
        audio.volume = value;
    }
});


// Prevent playback-rate changes

audio.addEventListener("ratechange", () => {
    if (audio.playbackRate !== 1) {
        audio.playbackRate = 1;
    }
});


// Prevent viewer seeking

audio.addEventListener("seeking", () => {
    if (Math.abs(audio.currentTime - lastAllowedPosition) > 0.5) {
        audio.currentTime = lastAllowedPosition;
    }
});


// Prevent viewer pausing

audio.addEventListener("pause", async () => {
    if (audio.srcObject && !audio.ended) {
        try {
            await audio.play();
        } catch {
            status.textContent = "CLICK PAGE TO START AUDIO";
        }
    }
});


// WebRTC

async function connectWebRTC() {
    console.log("[WEBRTC] Connecting...");
    status.textContent = "CONNECTING";

    peerConnection = new RTCPeerConnection({
        iceServers: [
            {
                urls: "stun:stun.l.google.com:19302"
            }
        ]
    });

    // Receive-only audio

    peerConnection.addTransceiver("audio", {
        direction: "recvonly"
    });

    // Remote track

    peerConnection.ontrack = async (event) => {
        console.log("[WEBRTC] Audio track received");
        console.log("Track:", event.track);

        if (event.track.kind !== "audio") {
            return;
        }

        const stream = new MediaStream([event.track]);

        audio.srcObject = stream;
        audio.volume = Number(volume.value);
        audio.playbackRate = 1.0;
        audio.defaultPlaybackRate = 1.0;

        try {
            await audio.play();
            status.textContent = "LIVE";
        } catch (error) {
            console.warn("[AUDIO] Autoplay blocked", error);
            status.textContent = "CLICK PAGE TO START AUDIO";
        }
    };

    // Connection state

    peerConnection.onconnectionstatechange = () => {
        console.log("[WEBRTC] Connection:", peerConnection.connectionState);

        switch (peerConnection.connectionState) {
            case "connected":
                status.textContent = "LIVE";
                break;

            case "connecting":
                status.textContent = "CONNECTING";
                break;

            case "disconnected":
                status.textContent = "DISCONNECTED";
                break;

            case "failed":
                status.textContent = "WEBRTC_FAILED";
                break;

            case "closed":
                status.textContent = "CLOSED";
                break;
        }
    };

    // ICE

    peerConnection.oniceconnectionstatechange = () => {
        console.log("[WEBRTC] ICE:", peerConnection.iceConnectionState);
    };

    // Create offer

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    // Wait for ICE

    await waitForIceGathering();

    // Send offer to Python

    const response = await fetch(`/api/rooms/${roomId}/webrtc/offer`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            type: peerConnection.localDescription.type,
            sdp: peerConnection.localDescription.sdp
        })
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    const answer = await response.json();

    await peerConnection.setRemoteDescription({
        type: answer.type,
        sdp: answer.sdp
    });

    console.log("[WEBRTC] Remote description set");
}


// ICE gathering

function waitForIceGathering() {
    if (peerConnection.iceGatheringState === "complete") {
        return Promise.resolve();
    }

    return new Promise((resolve) => {
        function checkState() {
            if (peerConnection.iceGatheringState === "complete") {
                peerConnection.removeEventListener("icegatheringstatechange", checkState);
                resolve();
            }
        }

        peerConnection.addEventListener("icegatheringstatechange", checkState);
    });
}


// Server position
async function updateServerPosition() {
    try {
        const response = await fetch(`/api/rooms/${roomId}`);

        if (response.status === 404) {
            console.error(`[ROOM] Room ${roomId} does not exist`);
            status.textContent = "ROOM NOT FOUND";
            return false;
        }

        if (!response.ok) {
            throw new Error(
                `Room request failed: ${response.status}`
            );
        }

        const data = await response.json();

        if (data.error === "NOT_PLAYING_ANYTHING_CURRENTLY") {
            status.textContent = "NOT PLAYING";
            return true;
        }

        if (typeof data.position === "number") {
            serverPosition = data.position;
            lastAllowedPosition = data.position;
        }

        return true;

    } catch (error) {
        console.error("Could not get room state:", error);
        status.textContent = "ROOM ERROR";
        return false;
    }
}

// Keep browser playback rate at normal speed

setInterval(() => {
    if (audio.playbackRate !== 1) {
        audio.playbackRate = 1;
    }
}, 500);


let stateInterval = null;

async function initialize() {
    if (!roomId) {
        status.textContent = "INVALID ROOM";
        return;
    }

    const exists = await updateServerPosition();

    if (!exists) {
        return;
    }

    try {
        await connectWebRTC();
    } catch (error) {
        console.error("[WEBRTC] Connection failed:", error);
        status.textContent = "WEBRTC_FAILED";
        return;
    }

    stateInterval = setInterval(updateServerPosition, 2000);
}

initialize();
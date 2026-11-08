import ipaddress

from aiohttp import web
from aiortc.sdp import candidate_from_sdp

from pyLiveMusic._logger import logs
from _api._errors import client_ip, read_json
from _utils._settings import MAX_CANDIDATES_PER_PEER, MAX_SDP_BYTES


async def offer(request):
    try:
        room_id = request.match_info["room_id"]

        manager = request.app["state"].rooms
        options = request.app["options"]

        room = manager.get(room_id)

        if room is None:
            raise web.HTTPNotFound(text="Room not found")

        data = await read_json(request)

        sdp = data.get("sdp")

        if (
            not isinstance(sdp, str)
            or not sdp
            or len(sdp) > MAX_SDP_BYTES
            or "m=audio" not in sdp
        ):
            raise web.HTTPBadRequest(text="Invalid SDP")

        remote = client_ip(request, options.trust_proxy)

        if (
            options.max_peers_total
            and manager.total_peers() >= options.max_peers_total
        ):
            raise web.HTTPServiceUnavailable(text="SERVER_BUSY")

        if (
            options.max_peers_per_ip
            and manager.peers_from(remote) >= options.max_peers_per_ip
        ):
            raise web.HTTPTooManyRequests(text="TOO_MANY_CONNECTIONS")

        try:
            peer = await room.add_peer(remote=remote)

        except ValueError:
            raise web.HTTPServiceUnavailable(text="ROOM_FULL")

        try:
            answer = await room.offer(peer, sdp)

        except ValueError:
            await room.remove_peer(peer)
            raise web.HTTPBadRequest(text="Invalid SDP")

        except Exception:
            await room.remove_peer(peer)
            raise

        return web.json_response({
            "peer_id": peer.id,
            "type": answer.type,
            "sdp": answer.sdp,
        })

    except web.HTTPException:
        raise

    except Exception:
        logs.exception("[WEBRTC] Offer error")
        raise


def _usable_candidate(ice, allow_private):
    """False for candidates the server must not send packets to.

    A candidate is an address the server will contact. Accepting loopback,
    LAN or link-local addresses (or hostnames) from an anonymous client
    turns the server into a scanner of its own network.
    """
    if allow_private:
        return True

    try:
        address = ipaddress.ip_address(ice.ip)

    except ValueError:
        return False  # hostname / mDNS name

    return address.is_global and 0 < ice.port < 65536


async def candidate(request):
    try:
        room_id = request.match_info["room_id"]

        room = request.app["state"].rooms.get(room_id)

        if room is None:
            raise web.HTTPNotFound(
                text="Room not found"
            )

        data = await read_json(request)

        peer_id = data.get("peer_id")

        if not peer_id or not isinstance(peer_id, str):
            raise web.HTTPBadRequest(
                text="Missing peer_id"
            )

        peer = room.get_peer(peer_id)

        if peer is None:
            raise web.HTTPNotFound(
                text="Peer not found"
            )

        value = data.get("candidate")

        if not value:
            return web.json_response({
                "ok": True
            })

        if not isinstance(value, dict):
            raise web.HTTPBadRequest(text="Invalid candidate")

        candidate_sdp = value.get("candidate")

        if not candidate_sdp:
            return web.json_response({
                "ok": True
            })

        if not isinstance(candidate_sdp, str) or len(candidate_sdp) > 512:
            raise web.HTTPBadRequest(text="Invalid candidate")

        try:
            ice = candidate_from_sdp(candidate_sdp)

        except Exception:
            raise web.HTTPBadRequest(
                text="Invalid ICE candidate"
            )

        if (
            peer.candidates_added >= MAX_CANDIDATES_PER_PEER
            or not _usable_candidate(
                ice,
                request.app["options"].allow_private_candidates,
            )
        ):
            # Not an error for the browser: it simply cannot be used.
            return web.json_response({
                "ok": True
            })

        mid = value.get("sdpMid")
        index = value.get("sdpMLineIndex")

        ice.sdpMid = mid if isinstance(mid, str) else None
        ice.sdpMLineIndex = index if isinstance(index, int) else None

        peer.candidates_added += 1

        await peer.add_candidate(ice)

        return web.json_response({
            "ok": True
        })

    except web.HTTPException:
        raise

    except Exception:
        logs.exception("[WEBRTC] Candidate error")
        raise

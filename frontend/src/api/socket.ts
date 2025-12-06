import { io } from "socket.io-client";

const socket = io(import.meta.env.VITE_BASE_API_URL, {
    autoConnect: true,
    transports: ["websocket"],
    withCredentials: true
});

export default socket;

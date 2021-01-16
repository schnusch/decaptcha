// Type definitions for npm packaga socksv5
// not nearly complete but good enough for us

declare module 'socksv5' {
	import * as net from 'net'

	type RequestInfo = {
		cmd:     string,
		dstAddr: string,
		dstPort: number,
	}

	type Listener = (
		info:   RequestInfo,
		accept: () => void,
		deny:   () => void,
	) => void

	class Server {
		on(event: 'connection', callback: Listener): this
		constructor()
		useAuth(auth: any): void
		listen(port: number, addr: string, ready: () => void): void
		close(callback?: () => void): void
		address(): net.AddressInfo | string | null
		readonly _srv: net.Server
	}

	export function createServer(listener: Listener): Server
	export const auth: {
		None: () => any,
	}
}

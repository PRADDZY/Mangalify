"""HTTP server for Prometheus metrics endpoint."""

import asyncio
from aiohttp import web
from prometheus_client import REGISTRY, generate_latest


async def metrics_handler(request):
    """Prometheus metrics endpoint handler."""
    return web.Response(
        body=generate_latest(REGISTRY),
        content_type='text/plain; version=0.0.4; charset=utf-8'
    )


async def health_handler(request):
    """Health check endpoint."""
    return web.json_response({'status': 'ok'})


async def start_metrics_server(port: int = 8000):
    """Start the metrics HTTP server.
    
    Args:
        port: Port to serve metrics on (default 8000)
    """
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)
    app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Prometheus metrics server started on port {port}")
    print(f"Access metrics at http://localhost:{port}/metrics")
    
    return runner


def run_metrics_server(port: int = 8000):
    """Blocking wrapper to run metrics server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def serve():
        runner = await start_metrics_server(port)
        try:
            # Keep server running indefinitely
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            await runner.cleanup()
    
    loop.run_until_complete(serve())

import asyncio
import uvicorn
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

def get_sse_packet(json_data: str):
    """Get an SSE packet."""
    return f"data: {json_data}\n\n"

# Completions endpoint
@app.get("/stream")
async def stream_output(request: Request):
    async def generator():
        try:
            for i in range(10):
                if await request.is_disconnected():
                    print("Disconnect triggered!")
                    break

                await asyncio.sleep(1)

                yield get_sse_packet(json.dumps({'testnum': i}))
        except asyncio.CancelledError:
            # Here, the print gets logged, then the exception gets sent as well
            print("Cancelled exception triggered!")
        except Exception:
            print(
                "Exception triggered!"
            )

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
    )


def start():
    uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
        )


if __name__ == "__main__":
    start()
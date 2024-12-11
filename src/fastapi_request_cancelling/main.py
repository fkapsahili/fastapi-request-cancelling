import asyncio
import uvicorn
import json
from fastapi import FastAPI, Request
from sse_starlette import EventSourceResponse
import anyio

app = FastAPI()

def get_sse_packet(json_data: str):
    """Get an SSE packet."""
    return f"data: {json_data}\n\n"


async def handle(send_chan):
    async with send_chan:
        try:
            for i in range(100):
                await send_chan.send(i)
                await asyncio.sleep(1)
        except anyio.ClosedResourceError:
            print("Closed!")

# Completions endpoint
@app.get("/stream")
async def stream_output(request: Request):
    send_chan, recv_chan = anyio.create_memory_object_stream(100)

    async def event_publisher():
        async with send_chan:
            task = asyncio.create_task(handle(send_chan))
            try:
                async for msg in recv_chan:
                    yield get_sse_packet(json.dumps({'testnum': msg}))
                await task
                if task.exception():
                    raise Exception("Task failed!")
            except asyncio.CancelledError:
                print("Cancelled exception triggered!")
            except Exception as e:
                print(
                    "Exception triggered!", e
                )
    return EventSourceResponse(event_publisher())



def start():
    uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
        )


if __name__ == "__main__":
    start()
from pathlib import Path
import aiofiles


class Download:
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def stream_download(self, resp, req):
        file = Path(self.file_path)

        if not file.exists():
            raise FileNotFoundError(f"couldn't find {self.file_path}")

        resp.headers['Content-Disposition'] = f'attachment; filename="{file.name}"'

        await resp.prepare(req)

        # Iterate over the data and write it to the response
        async with aiofiles.open(str(file), 'rb') as f:
            while True:
                chunk = await f.read(4096)  # Read chunks of 4096 bytes
                if not chunk:
                    break
                await resp.write(chunk)

        return resp

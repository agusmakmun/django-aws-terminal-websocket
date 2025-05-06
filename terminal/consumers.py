import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import asyncssh
import logging
import os
from terminal.otel_tracing import traced_async_class

logger = logging.getLogger(__name__)


HOSTNAME: str = os.getenv(
    "AWS_HOSTNAME",
    default="ec2-xxxx.us-west-1.compute.amazonaws.com",
)
USERNAME: str = os.getenv("AWS_USERNAME", default="xxxx")
KEY_PATH: str = os.path.join(os.path.dirname(__file__), "aws.pem")
PORT: int = 22


@traced_async_class
class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connect: id={id(self)}")
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"message": "WebSocket connected. Starting EC2 session..."}
            )
        )
        self.ssh_task = asyncio.create_task(self.ssh_to_ec2())
        self.process = None
        self.conn = None
        self.first_time = False

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: id={id(self)}, code={close_code}")
        if hasattr(self, "ssh_task"):
            self.ssh_task.cancel()
        if self.process:
            self.process.terminate()
        if self.conn:
            self.conn.close()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data is not None:
            print(f"BYTES RECEIVED: {bytes_data!r}")
        if text_data is not None:
            print(f"TEXT RECEIVED: {text_data!r}")
        if self.process:
            # make new line for the first time
            if not self.first_time:
                self.process.stdin.write("\n")
                self.first_time = True

            if bytes_data is not None:
                self.process.stdin.write(bytes_data.decode("utf-8", errors="ignore"))
            elif text_data is not None:
                self.process.stdin.write(text_data)
            await self.process.stdin.drain()

    async def ssh_to_ec2(self):
        try:
            logger.info(
                f"Connecting to EC2: {USERNAME}@{HOSTNAME}:{PORT} with key {KEY_PATH}"
            )
            self.conn = await asyncssh.connect(
                HOSTNAME,
                username=USERNAME,
                client_keys=[KEY_PATH],
                port=PORT,
                known_hosts=None,
            )
            self.process = await self.conn.create_process(
                term_type="vt100",
                term_size=(80, 24),
            )
            await self.send(
                text_data=json.dumps({"message": f"Connected to {HOSTNAME}"})
            )
            logger.info(f"SSH session established to {HOSTNAME}")
            while not self.process.stdout.at_eof():
                data = await self.process.stdout.read(4096)
                if data:
                    logger.debug(f"EC2 output: {data}")
                    await self.send(bytes_data=data.encode("utf-8"))
        except Exception as e:
            logger.error(f"SSH error: {str(e)}")
            await self.send(text_data=json.dumps({"message": f"SSH error: {str(e)}"}))
        finally:
            if self.process:
                self.process.terminate()
            if self.conn:
                self.conn.close()
            logger.info("SSH session closed")

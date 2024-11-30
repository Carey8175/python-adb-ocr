import psutil
import asyncio

from loguru import logger
from paddleocr import PaddleOCR
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.adb_device_async import AdbDeviceTcpAsync


class AdbOCR:
    def __init__(self):
        self._device: AdbDeviceTcpAsync|None = None
        self.ocr_engine = PaddleOCR()

    async def load(self, port: int, host: str = "localhost", scan_if_fail=True) -> None:
        """
        Load the ADB connection.

        Args:
            port: The port to connect to.
            host: The host to connect to.
            scan_if_fail: Whether to scan for local devices if the connection fails.

        Returns:
        """
        task1 = asyncio.create_task(self._init_ocr_engine())
        task2 = asyncio.create_task(self._connect_device(port=port, host=host, scan_if_fail=scan_if_fail))

        await task1
        await task2

    async def _connect_device(self, port: int, host: str = "localhost", scan_if_fail: bool = True) -> None:
        """
        Connect to the device.

        Args:
            port: The port to connect to.
            host: The host to connect to.
            scan_if_fail: Whether to scan for devices if the connection fails.

        Returns:
        """
        if self._device is not None:
            return

        device = AdbDeviceTcpAsync(host=host, port=port, default_transport_timeout_s=9)
        logger.debug(f"Connecting to Device[{host}:{port}]...")

        try:
            connection = await device.connect()
            if connection:
                self._device = device
                return
        except OSError:
            logger.warning(f"[X]Failed to connect to Device[{host}:{port}].")

        # scan for devices at localhost if the connection failed
        if host == "localhost" and scan_if_fail:
            # scan the local devices
            port_found = await self._scan_local_devices()

            if port_found:
                try:
                    connection = await self._connect_device(port=port_found, host=host, scan_if_fail=False)
                    if connection:
                        self._device = device
                        return
                except OSError:
                    pass

        logger.warning(
            f"Failed to connect to emulator, please make sure the ADB is enabled on your emulator.")

    async def _scan_local_devices(self) -> int | None:
        """
        Scan for devices at localhost.

        Returns: the open adb ports or None if no device was found.
        """
        logger.info("Scanning for open adb devices at localhost...")

        connections = [
            conn for conn in psutil.net_connections("tcp4") if conn.laddr.port >= 5555 and conn.status == "LISTEN"
        ]

        logger.warning(f"There are {len(connections)} open ports, trying to find the abd port.")

        for conn in connections:
            logger.debug(f"Scanning port {conn.laddr.port} for ADB...")
            try:
                adb_device = AdbDeviceTcp("localhost", port=conn.laddr.port, default_transport_timeout_s=0.5)
                if adb_device.connect(read_timeout_s=0.5):
                    adb_device.close()
                    return conn.laddr.port
            # Reason for disable: The code above can throw a lot of different exceptions, this is the simplest solution.
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.debug(f"Port {conn.laddr.port} threw '{e}'.")

        logger.warning("No local device was found. Make sure ADB is enabled in your emulator's settings.")
        return None

    async def _init_ocr_engine(self) -> None:
        """
        Initialize the OCR engine.

        Returns:
        """
        self.ocr_engine = PaddleOCR(lang='ch')

    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
        """
        return self._device and self._device.available

    async def get_screen_size(self) -> tuple[int, int]:
        """
        Get the screen size.

        Returns:
            (width, height) of the screen.
        """
        if not self.is_connected():
            return 0, 0

        shell_output = await self._device.shell("wm size | awk 'END{print $3}'")
        return shell_output.replace("\n", "")

    async def get_screen_density(self) -> int:
        """
        Get the screen density.

        Returns:
             the number of pixels per inch.
        """
        shell_output = await self._device.shell("wm density | awk 'END{print $3}'")
        return shell_output.replace("\n", "")

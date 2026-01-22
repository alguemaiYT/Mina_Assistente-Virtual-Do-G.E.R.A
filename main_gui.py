#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal GUI Launcher for Xiaozhi AI Client (GUI-only version)

This launcher starts only the GUI display without any backend services.
Ideal for testing and developing the GUI components in isolation.
"""

import asyncio
import sys
import os
import signal

# Configure Qt platform before importing Qt
is_wayland = (
    os.environ.get("WAYLAND_DISPLAY")
    or os.environ.get("XDG_SESSION_TYPE") == "wayland"
)

if is_wayland and "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
    os.environ.setdefault("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")

try:
    import qasync
    from PyQt5.QtWidgets import QApplication
except ImportError as e:
    print(f"ERROR: GUI mode requires qasync and PyQt5: {e}")
    print("Please install: pip install PyQt5 qasync")
    sys.exit(1)

from src.display.gui_display import GuiDisplay
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


async def run_gui():
    """
    Run the GUI display in standalone mode.
    """
    logger.info("Starting Xiaozhi GUI (standalone mode)")
    
    try:
        # Create and start the GUI display
        gui_display = GuiDisplay()
        
        # Set minimal callbacks (optional - can be expanded for testing)
        await gui_display.set_callbacks(
            auto_callback=lambda: logger.info("Auto mode toggled"),
            abort_callback=lambda: logger.info("Aborted"),
            send_text_callback=lambda text: logger.info(f"Text sent: {text}"),
        )
        
        # Start the GUI
        await gui_display.start()
        
        # Set initial status
        await gui_display.update_status("GUI Ready (standalone mode)", True)
        await gui_display.update_emotion("neutral")
        
        logger.info("GUI started successfully")
        
        # Keep the event loop running until GUI is closed
        while gui_display._running:
            await asyncio.sleep(0.1)
            
    except Exception as e:
        logger.error(f"GUI error: {e}", exc_info=True)
        return 1
    
    return 0


def main():
    """
    Main entry point for the GUI-only launcher.
    """
    exit_code = 1
    
    try:
        # Setup logging
        setup_logging()
        
        # Handle signals
        try:
            if hasattr(signal, "SIGTRAP"):
                signal.signal(signal.SIGTRAP, signal.SIG_IGN)
        except Exception:
            pass
        
        # Create Qt application
        qt_app = QApplication.instance() or QApplication(sys.argv)
        qt_app.setQuitOnLastWindowClosed(False)
        
        # Create qasync event loop
        loop = qasync.QEventLoop(qt_app)
        asyncio.set_event_loop(loop)
        logger.info("Created qasync event loop")
        
        # Run the GUI
        with loop:
            exit_code = loop.run_until_complete(run_gui())
            
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        exit_code = 0
    except Exception as e:
        logger.error(f"Program exited with error: {e}", exc_info=True)
        exit_code = 1
    finally:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()

"""Entry point for Organismo Vivo - Bio-Digital System."""
import asyncio
import logging
from pathlib import Path
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

async def main():
    """Main entry point for Organismo Vivo."""
    logger.info("organismo_vivo_starting", version="100.0")
    
    # Import bio-digital system
    from core.system.bio_digital import SistemaBioDigital, SystemConfig
    
    # Load configuration
    config_path = Path(__file__).parent / "config" / "bio_config.yaml"
    
    try:
        if config_path.exists():
            config = SystemConfig.from_yaml(str(config_path))
            logger.info("config_loaded_from_yaml", path=str(config_path))
        else:
            # Use default config
            config = SystemConfig()
            logger.warning("config_file_not_found_using_defaults", path=str(config_path))
    except Exception as e:
        logger.error("config_load_failed_using_defaults", error=str(e))
        config = SystemConfig()
    
    # Initialize system
    system = SistemaBioDigital(config)
    
    try:
        # Bootstrap all subsystems
        await system.bootstrap()
        
        # Example: Process test event
logger.info("processing_test_event")
        result = await system.process_event(
            b'test_payload_for_immune_system' * 10,
            source_id='main_entry_point'
        )
        logger.info("test_event_result", result=result)
        
        if result['success']:
            logger.info("organismo_vivo_running", message="System is alive and processing events")
        
        # Keep system alive (replace with actual event loop in production)
        logger.info("keeping_system_alive", duration_seconds=60)
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt_received")
    except Exception as e:
        logger.error("system_error", error=str(e), exc_info=True)
    finally:
        # Graceful shutdown
        await system.shutdown()
        logger.info("organismo_vivo_stopped")

if __name__ == '__main__':
    asyncio.run(main())

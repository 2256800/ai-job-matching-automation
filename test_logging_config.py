from logging_config import LOG_FILE, logger

def test_logging_configuration():
    logger.info("Logging configuration test")

    assert LOG_FILE.exists()
    assert logger.level == 20  # logging.INFO
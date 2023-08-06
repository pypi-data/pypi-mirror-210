from . import dashBoard

__version__ = "0.0.8"


def dash_board():
    """Launches the dash board."""
    dashBoard.main()


def getShipments():
    """getShipments."""
    from .getShipments import main
    main()


def glueWeight():
    """glue weight."""
    from .GlueWeight import main
    main()


def groundingTest():
    """GND/VI tests."""
    from .groundingTest import main
    main()


def sendShipments():
    """Send items."""
    from .sendShipments import main
    main()


def uploadTest():
    """Upload tests."""
    from .uploadTest import main
    main()


def uploadMultipleTests():
    """Upload multiple tests."""
    from .uploadMultipleTests import main
    main()

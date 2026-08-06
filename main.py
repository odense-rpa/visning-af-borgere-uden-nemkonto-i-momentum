import asyncio
from datetime import datetime
import logging
import sys
from ky_client import KYClientManager
from odk_tools.tracking import Tracker
from odk_tools.reporting import report
from momentum_client.manager import MomentumClientManager
from automation_server_client import AutomationServer, Workqueue, WorkItemError, Credential, WorkItemStatus

ky: KYClientManager
momentum: MomentumClientManager
tracker: Tracker
proces_navn = "Visning af borgere uden NemKonto i Momentum"


def populate_queue(workqueue: Workqueue):
    logger = logging.getLogger(__name__)

    logger.info("Hello from populate workqueue!")
    opgaver = ky.opgaveindbakke.hent_opgaver("KH - 22. Liste nemkonto")

    for opgave in opgaver:
        data = {
            "cpr": opgave["CPR-nummer"],
            "navn": opgave["Navn"],
        }
        workqueue.add_item(data=data, reference=data["cpr"])


def process_workqueue(workqueue: Workqueue):
    logger = logging.getLogger(__name__)

    logger.info("Hello from process workqueue!")

    for item in workqueue:
        with item:
            data = item.data  # Item data deserialized from json as dict
 
            try:
                cpr_uden_bindestreg = data["cpr"].replace("-", "")
                borger = momentum.borgere.hent_borger(cpr=cpr_uden_bindestreg)
                if borger is None:
                    continue  # Skip, borger findes ikke i Momentum

                # Check om borger allerede har en markering for manglende NemKonto
                borgers_markeringer = momentum.borgere.hent_markeringer(borger)
                nemkonto_markering = next(
                    (m for m in borgers_markeringer if m["tag"]["title"] == "Borger har ikke NemKonto" and m["tag"]["end"] is None), None
                )
                if nemkonto_markering:
                    continue # Skip, borger har allerede markering for manglende NemKonto

                momentum.borgere.opret_markering( 
                    markeringsnavn="Borger har ikke NemKonto",
                    borger=borger,
                    start_dato=datetime.now().date(),
                )
                tracker.track_task(process_name=proces_navn)

            except WorkItemError as e:
                # A WorkItemError represents a soft error that indicates the item should be passed to manual processing or a business logic fault
                logger.error(f"Error processing item: {data}. Error: {e}")
                item.fail(str(e))


if __name__ == "__main__":
    ats = AutomationServer.from_environment()
    workqueue = ats.workqueue()

    # Initialize external systems for automation here..
    roboa = Credential.get_credential("RoboA")
    tracking_credential = Credential.get_credential("Odense SQL Server")

    tracker = Tracker(
        username=tracking_credential.username, password=tracking_credential.password
    )    

    momentum_credential = Credential.get_credential("Momentum - produktion")
    momentum = MomentumClientManager(
        base_url=momentum_credential.data["base_url"],
        client_id=momentum_credential.username,
        client_secret=momentum_credential.password,
        api_key=momentum_credential.data["api_key"],
        resource=momentum_credential.data["resource"],
        timeout=90.0
    )

    # Queue management
    if "--queue" in sys.argv:
        ky = KYClientManager(
            username=f"{roboa.username}@odense.dk",
            password=roboa.password,
            idp=roboa.data["idp"],
        )
        workqueue.clear_workqueue(WorkItemStatus.NEW)
        populate_queue(workqueue)
        exit(0)

    # Process workqueue
    process_workqueue(workqueue)

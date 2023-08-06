"""cli interface for gallagher restapi."""
import argparse
import asyncio
import logging
import os
from datetime import datetime

import httpx

import gallagher_restapi
from gallagher_restapi.models import (
    FTCardholder,
    FTCardholderCard,
    FTItemReference,
    FTStatus,
    PatchAction,
)

_LOGGER = logging.getLogger(__name__)


async def main(host: str, port: int, api_key: str) -> None:
    """Test connecting to Gallagher REST api."""

    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.authenticate()
            await client.get_item_types()
            # if divisions := await client.get_item(
            #     client.item_types["Division"], "ICAD"
            # ):
            #     _LOGGER.info(divisions[0])
            # new_cardholder = FTCardholder(
            #     firstName="Rami",
            #     lastName="1",
            #     division=FTItemReference(href=divisions[0].href),
            # )
            # if await cardholder_client.add_cardholder(new_cardholder):
            #     _LOGGER.info("New cardholder created successfully.")
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)

    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.authenticate()
            if doors := await client.get_door(
                name="leb", extra_fields=["defaults", "division", "statusFlags"]
            ):
                _LOGGER.info(len(doors))
            if cardholders := await client.get_cardholder(
                extra_fields=["defaults", "cards"]
            ):
                _LOGGER.info(
                    "Successfully connected to Gallagher server"
                    "and retrieved %s cardholders",
                    len(cardholders),
                )
            # update cardholder
            cardholder = [
                cardholder
                for cardholder in cardholders
                if cardholder.firstName == "Rami" and cardholder.lastName == "Mousleh"
            ][0]
            cardholder_card: FTCardholderCard = cardholder.cards[0]
            cardholder_card.status = FTStatus(value="active")
            cardholder_card.active_until = datetime(2023, 5, 20)
            remove_card = cardholder.cards[-1]
            remove_card.status = FTStatus(value="Stolen")
            updated_cardholder = FTCardholder.patch(
                cardholder,
                cards={
                    PatchAction.UPDATE: [cardholder_card],
                    PatchAction.REMOVE: [remove_card],
                },
                pdfs={"Mobile1": "+0987654321"},
            )
            if await client.update_cardholder(updated_cardholder):
                _LOGGER.info(f"Cardholder id {cardholder.id} was updated successfully")
            remove_cardholder = [
                cardholder
                for cardholder in cardholders
                if cardholder.firstName == "Rami" and cardholder.lastName == "1"
            ][0]
            if await client.remove_cardholder(remove_cardholder):
                _LOGGER.info(
                    f"Cardholder id {remove_cardholder.id} was removed successfully"
                )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)
    try:
        async with httpx.AsyncClient(verify=False) as httpx_client:
            client = gallagher_restapi.Client(
                host=host,
                port=port,
                api_key=api_key,
                httpx_client=httpx_client,
            )
            await client.authenticate()
            event_filter = gallagher_restapi.EventFilter(
                top=1,
                previous=True,
            )
            last_event = await client.get_events(event_filter=event_filter)
            _LOGGER.info(
                "Successfully connected to Gallagher server "
                "and retrieved the last event: %s",
                last_event[0].message,
            )
    except gallagher_restapi.GllApiError as err:
        _LOGGER.error(err)


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-api_key", help="Gallagher API Key", type=str, default=os.getenv("API_KEY")
    )
    parser.add_argument("-host", type=str, default=os.getenv("HOST") or "localhost")
    parser.add_argument("-p", "--port", type=int, default=os.getenv("PORT") or 8904)
    parser.add_argument("-D", "--debug", action="store_true")
    arguments = parser.parse_args()

    LOG_LEVEL = logging.INFO
    if arguments.debug:
        LOG_LEVEL = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=LOG_LEVEL)

    return arguments


if __name__ == "__main__":
    args = get_arguments()
    try:
        asyncio.run(main(host=args.host, port=args.port, api_key=args.api_key))
    except KeyboardInterrupt:
        pass

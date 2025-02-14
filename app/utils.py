import csv
import io
import logging
import os

from flask import Response

logger = logging.getLogger(__name__)


def get_environment() -> str:
    return os.environ.get('ENVIRONMENT', 'DEV')


def generate_csv(data, filename) -> Response:
    if not data or not isinstance(data, list) or not all(
            isinstance(item, dict) for item in data):
        logger.warning("Invalid or missing data provided for CSV generation.")
        return Response("Invalid or missing data",
                        status=400,
                        mimetype="text/plain")

    try:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        local_filepath = os.path.join(os.getcwd(), f"{filename}.csv")
        with open(local_filepath, "w", newline="", encoding="utf-8") as file:
            file.write(buffer.getvalue())

        logger.info(f"CSV file '{filename}.csv' generated successfully.")

        return Response(buffer.getvalue(),
                        mimetype="text/csv",
                        headers={
                            "Content-Disposition":
                            f"attachment; filename={filename}.csv",
                            "Cache-Control":
                            "no-cache, no-store, must-revalidate",
                            "Pragma": "no-cache",
                            "Expires": "0"
                        })

    except Exception as error:
        logger.error(f"Error generating CSV: {error}", exc_info=True)
        return Response("Serviço não disponível",
                        status=503,
                        mimetype="text/plain")

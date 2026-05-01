import os
import logging
import requests

logger = logging.getLogger(__name__)

ROBOFLOW_UPLOAD_URL = "https://api.roboflow.com/dataset/{project}/upload"


def upload_for_review(image_path, project_id, api_key, split="train"):
    """Push a low-confidence image into the Roboflow dataset's unassigned queue
    so a human can re-label it. Best-effort: failures are logged, not raised.
    """
    if not os.path.isfile(image_path):
        logger.warning("Cannot upload missing file %s", image_path)
        return False

    project_slug = project_id.split("/")[-1]
    url = ROBOFLOW_UPLOAD_URL.format(project=project_slug)
    name = os.path.basename(image_path)

    with open(image_path, "rb") as fh:
        files = {"file": (name, fh, "image/jpeg")}
        params = {"api_key": api_key, "name": name, "split": split}
        try:
            resp = requests.post(url, params=params, files=files, timeout=15)
        except requests.RequestException as exc:
            logger.error("Roboflow upload network error for %s: %s", name, exc)
            return False

    if resp.status_code >= 400:
        logger.error("Roboflow upload failed (%s): %s", resp.status_code, resp.text[:300])
        return False

    logger.info("Uploaded %s to Roboflow dataset for review", name)
    return True

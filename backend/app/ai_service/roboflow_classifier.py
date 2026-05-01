import os
import logging
from PIL import Image, ImageDraw, ImageFont
from inference_sdk import InferenceHTTPClient

from roboflow_uploader import upload_for_review

logger = logging.getLogger(__name__)

ALLOWED_PALLET_TYPES = {"euro", "EPAL", "Other"}
FALLBACK_PALLET_TYPE = "Other"


class RoboflowClassifier:
    def __init__(self, api_key, project_id, version, threshold, output_dir,
                 upload_low_conf=True):
        if not api_key or not project_id or not version:
            raise ValueError("ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_ID and ROBOFLOW_MODEL_VERSION must be set")
        self.api_key = api_key
        self.project_id = project_id
        self.version = str(version)
        self.threshold = float(threshold)
        self.output_dir = output_dir
        self.upload_low_conf = upload_low_conf
        self.model_id = f"{self.project_id}/{self.version}"
        self.client = InferenceHTTPClient(
            api_url="https://classify.roboflow.com",
            api_key=self.api_key,
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def run_inference(self, image_path):
        if not os.path.isfile(image_path):
            return {"error": "Image not found"}, 404

        raw = self.client.infer(image_path, model_id=self.model_id)

        label, confidence = self._extract_top_prediction(raw)
        if label is None:
            return {"error": "No prediction returned by Roboflow"}, 502

        mapped_label = label if label in ALLOWED_PALLET_TYPES else FALLBACK_PALLET_TYPE
        if mapped_label != label:
            logger.warning(
                "Roboflow class %r is not a known PalletType; coerced to %r. "
                "Align Roboflow class names with PalletType seed values.",
                label, mapped_label,
            )

        flagged = confidence < self.threshold
        annotated_path = self._annotate(image_path, mapped_label, confidence)

        if flagged and self.upload_low_conf:
            try:
                upload_for_review(image_path, self.project_id, self.api_key)
            except Exception as exc:
                logger.error("Active-learning upload failed for %s: %s", image_path, exc)

        return {
            "label": mapped_label,
            "confidence": confidence,
            "model_version": self.version,
            "annotated_image_path": annotated_path,
            "flagged_for_review": flagged,
        }, 200

    @staticmethod
    def _extract_top_prediction(raw):
        if not isinstance(raw, dict):
            return None, None
        if "top" in raw and "confidence" in raw:
            return raw["top"], float(raw["confidence"])
        preds = raw.get("predictions")
        if isinstance(preds, dict) and preds:
            top_label = max(preds, key=lambda k: preds[k].get("confidence", 0))
            return top_label, float(preds[top_label].get("confidence", 0))
        if isinstance(preds, list) and preds:
            top = max(preds, key=lambda p: p.get("confidence", 0))
            return top.get("class"), float(top.get("confidence", 0))
        return None, None

    def _annotate(self, image_path, label, confidence):
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        text = f"{label} {confidence:.1%}"
        bbox = draw.textbbox((0, 0), text, font=font)
        pad = 6
        box = [0, 0, bbox[2] - bbox[0] + pad * 2, bbox[3] - bbox[1] + pad * 2]
        draw.rectangle(box, fill=(0, 0, 0))
        draw.text((pad, pad), text, fill=(255, 255, 255), font=font)
        out_path = os.path.join(self.output_dir, f"inferenced_{os.path.basename(image_path)}")
        img.save(out_path)
        return out_path

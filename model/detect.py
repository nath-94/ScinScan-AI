from ultralytics import YOLO
import uuid

def formater_resultats_yolo(results, image_width, image_height, class_names, output_image_b64=None):
    boxes = results[0].boxes
    predictions_list = []

    for i in range(len(boxes)):
        box = boxes.xywh[i].tolist()
        conf = float(boxes.conf[i])
        cls_id = int(boxes.cls[i])
        
        prediction = {
            "width": int(box[2]),
            "height": int(box[3]),
            "x": float(box[0]),
            "y": float(box[1]),
            "confidence": conf,
            "class_id": cls_id,
            "class": class_names[cls_id],
            "detection_id": str(uuid.uuid4()),
            "parent_id": "image"
        }
        predictions_list.append(prediction)

    resultat = {
        "count_objects": len(predictions_list),
        "output_image": output_image_b64 or None,
        "predictions": {
            "image": {
                "width": image_width,
                "height": image_height
            },
            "predictions": predictions_list
        }
    }

    return resultat


def detect(image_path:str):
    import os
    # Utiliser un chemin absolu pour le modèle
    model_path = os.path.join(os.path.dirname(__file__), "best.pt")
    model = YOLO(model_path)
    results = model(image_path)
    class_names = ["mole"]  # Ou plus de classes si tu en as
    image_height, image_width = results[0].orig_shape
    # Optionnel : si tu veux afficher une image encodée en base64
    output_image_b64 = None

    json_result = formater_resultats_yolo(results, image_width, image_height, class_names, output_image_b64)
    return [json_result]


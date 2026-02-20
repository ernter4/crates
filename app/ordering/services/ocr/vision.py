import io

from google.cloud import vision


def send_to_google(img):
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image = vision.Image(content=buffer.getvalue())


    image_context = vision.ImageContext(
        language_hints=["de"]
    )
    client_options = {"api_endpoint": "eu-vision.googleapis.com",}
    vision_client = vision.ImageAnnotatorClient(client_options=client_options)
    response = vision_client.document_text_detection(image=image, image_context=image_context)
    return response.text_annotations[1:]
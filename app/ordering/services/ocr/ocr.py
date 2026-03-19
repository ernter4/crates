import datetime
import io
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageColor, ImageDraw
from fastapi.responses import Response
from google.cloud.vision_v1 import TextAnnotation
from matplotlib.patches import Polygon
from numpy._core.strings import isnumeric

from sqlmodel import Session,select,func


from app.accounting.models import Customer
from app.ordering.models import CrateRecord, Crate

from app.ordering.services.ocr.vision import send_to_google

class OCR:
    def __init__(self,session,image):
        self.image:Image = image
        self.preprocessed_image:Optional[Image] = None
        self.text_annotations: list[TextAnnotation] = []
        self.box_annotations: list[TextAnnotation] = []
        self.session:Session= session
        self.records:list[CrateRecord]= []
    def preprocess_image(self):
        """
        Vorverarbeitung des Bildes:
        1. Rote Farben isolieren und verstärken
        2. Kontrast erhöhen
        3. Schärfen
        """

        # Konvertiere zu RGB falls nötig
        if self.image.mode != 'RGB':
            img = self.image.convert('RGB')
        else:
            img = self.image
        # Konvertiere zu numpy array für Farbfilterung
        img_array = np.array(img)

        # Rote Farben isolieren (R hoch, G und B niedrig)
        # Rote Bereiche haben hohen Rot-Wert und niedrige Grün/Blau-Werte
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

        # Maske für rote Bereiche: Rot > 150 UND (Rot > Grün + 50) UND (Rot > Blau + 50)
        red_mask = (r > 150) & (r > g + 50) & (r > b + 50)

        # Erstelle ein neues Bild mit nur den roten Bereichen
        red_only = np.zeros_like(img_array)
        red_only[red_mask] = [255, 255, 255]  # Weiß für rote Bereiche
        red_only[~red_mask] = [0, 0, 0]  # Schwarz für den Rest

        # Konvertiere zurück zu PIL Image
        processed = Image.fromarray(red_only)

        # Graustufen für bessere OCR
        # processed = processed.convert('L')

        # Kontrast erhöhen
        enhancer = ImageEnhance.Contrast(processed)
        processed = enhancer.enhance(2.0)

        # Schärfen
        processed = processed.filter(ImageFilter.SHARPEN)

        # Speichern
        self.preprocessed_image = processed

    def run_ocr(self):
        self.preprocess_image()
        with ThreadPoolExecutor(max_workers=2) as executor:
            prepocessed_future = executor.submit(send_to_google, self.preprocessed_image)
            initial_future = executor.submit(send_to_google, self.image)
            self.text_annotations = initial_future.result()
            box_annotations = prepocessed_future.result()
        for index ,annotation in enumerate(box_annotations):
            if  re.findall(r'\b\d\d\b', annotation.description):
                self.box_annotations.append(annotation)

    def extract_box_numbers(self, text_annotations) -> list[TextAnnotation]:
        matches = []
        annotations: list[TextAnnotation] = []

        for annotation in text_annotations:
            text = annotation.description
            match = re.findall(r'\b\d\d\b', text)
            if match:
                annotations.append(annotation)
                matches.append(match[0])

        return annotations

    def is_in_polygon(self, polygon: Polygon, block: TextAnnotation) -> bool:
        for vertex in block.bounding_poly.vertices:
            point = (vertex.x, vertex.y)
            if polygon.contains_point(point):
                return True
        return False

    def get_bounding_poly(self,shapes:list[list[tuple[int,int]]]) -> list[tuple[int,int]]:
        x_min=500000
        y_min=500000
        x_max=0
        y_max=0
        for shape in shapes:
            for point in shape:
                if point[0] < x_min:
                    x_min = point[0]
                elif point[0] > x_max:
                    x_max = point[0]
                if point[1] < y_min:
                    y_min = point[1]
                elif point[1] > y_max:
                    y_max = point[1]
        return [(x_min,y_min),(x_max,y_min),(x_max,y_max),(x_min,y_max)]

    def get_shape(self,annotation)->list[tuple[int,int]]:
        shape = []
        for vertex in annotation.bounding_poly.vertices:
            shape.append((vertex.x, vertex.y))
        return shape

    def interpret_crate(self,box:TextAnnotation) :
        crate  = self.session.get(Crate,int(box.description))
        if crate:
            record = CrateRecord(crate=crate)
        else :
            return
        record.shapes.append(self.get_shape(box))
        polygon = self.get_search_polygon(box)



        for textblock in self.text_annotations:
            if self.is_in_polygon(polygon, textblock):
                record.shapes.append(self.get_shape(textblock))
                if isnumeric(textblock.description.strip() ):
                    record.menu_id = int(textblock.description)
                else:
                    statement = select(Customer)
                    statement = statement.where(
                        func.lower(Customer.display_text).like(f"%{textblock.description.lower()}%")
                    )

                    customers =self.session.exec(statement).fetchall()
                    if len(customers)==1:
                        record.customer = customers[0]
                        record.shapes.append(self.get_bounding_poly(record.shapes))
        self.records.append(record)

    def draw_record(self,crate_id:int,color:ImageColor) -> None:
        found_record:CrateRecord
        for search_record in self.records:
            if search_record.crate.id == crate_id:
                found_record= search_record
                break
        drw = ImageDraw.Draw(self.image, 'RGBA')
        for shape in found_record.shapes:
            drw.polygon(xy=shape, outline=color,width=5)

    def get_search_polygon(self, box) -> Polygon:
        coordinates = box.bounding_poly.vertices
        # Horizontal
        vertical_delta_x = coordinates[1].x - coordinates[2].x
        vertical_delta_y = coordinates[1].y - coordinates[2].y
        horizontal_delta_x = coordinates[0].x - coordinates[1].x
        horizontal_delta_y = coordinates[0].y - coordinates[1].y


        coordinates[0].x += int(1 * vertical_delta_x) + int(4 * horizontal_delta_x)
        coordinates[0].y += int(1 * vertical_delta_y) + int(4 * horizontal_delta_y)
        coordinates[3].x += -int(0.5 * vertical_delta_x) + int(4 * horizontal_delta_x)
        coordinates[3].y += -int(0.5 * vertical_delta_y) + int(4 * horizontal_delta_y)

        coordinates[1].x += int(0.5 * vertical_delta_x) + int(horizontal_delta_x)
        coordinates[1].y += int(0.5 * vertical_delta_y) + int(horizontal_delta_y)
        coordinates[2].x += -int(0.5 * vertical_delta_x) + int(horizontal_delta_x)
        coordinates[2].y += -int(0.5 * vertical_delta_y) + int(horizontal_delta_y)

        points: list[tuple[int, int]] = []
        for coordinate in coordinates:
            points.append((coordinate.x, coordinate.y))
        polygon: Polygon = Polygon(points)

        return polygon

    def get_image_response(self):
        # PNG-Format encodieren
        buffer = io.BytesIO()
        self.image.save(buffer, format='PNG')
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="image/png")
    def process_image(self):
        self.run_ocr()
        for crate in self.box_annotations:
            self.interpret_crate(crate)




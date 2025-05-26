from flask import Blueprint, Response
from app import db
from app.models import NoteImage
import mimetypes

image_bp = Blueprint('image', __name__, url_prefix='/api')

@image_bp.route('/images/by-name/<filename>')
def get_image_by_name(filename):
    image = NoteImage.query.filter_by(image_url=filename).first()
    if image and image.image_data:
        mime = mimetypes.guess_type(image.image_url)[0]
        if not mime:
            mime = "application/octet-stream"  
        print(f"📷 Serving by name: {filename} | MIME: {mime}")
        return Response(image.image_data, mimetype=mime)
    return Response("Image not found", status=404)

@image_bp.route('/images/<int:image_id>')
def get_image_by_id(image_id):
    image = NoteImage.query.filter_by(id=image_id).first()
    if image and image.image_data:
        mime = mimetypes.guess_type(image.image_url)[0]
        if not mime:
            mime = "application/octet-stream"
        print(f"📷 Serving by id: {image_id} | MIME: {mime}")
        return Response(image.image_data, mimetype=mime)
    return Response("Image not found", status=404)

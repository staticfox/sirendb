import io

from flask import Blueprint, abort, send_file
from flask_login import login_required

from sirendb.models.siren_media import SirenMedia
from sirendb.lib.storage import storage

bp = Blueprint(__name__, template_directory=None)


@bp.route('/media/<string:filename>')
@login_required
def get_media(filename: str):
    media = SirenMedia.query.filter_by(
        filename=filename
    ).first()

    if not media:
        return abort(404, description='file not found')

    data = storage.get(media.filesystem_key)
    if data:
        fp = io.BytesIO(data)
        return send_file(fp, mimetype=media.mimetype)
    else:
        return abort(404, description='file not found')

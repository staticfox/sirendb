import io

from flask import Blueprint, abort, send_file
from flask_login import login_required

from sirendb.models.siren_media import SirenMedia
from sirendb.lib.storage import storage

bp = Blueprint('media', __name__)


@bp.route('/media/<string:filename>')
@login_required
def get_media(filename: str):
    media = SirenMedia.query.filter_by(
        filename=filename
    ).first()

    if not media:
        return abort(404, description='file not found')

    data = storage.get(media.filesystem_uri)
    if data:
        fp = io.BytesIO()
        fp.write(data)
        fp.seek(0)

        return send_file(
            fp,
            as_attachment=True,
            attachment_filename=media.filename,
            mimetype=media.mimetype,
        )
    else:
        return abort(404, description='file not found')

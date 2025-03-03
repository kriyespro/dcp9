from flask import jsonify, render_template, request, current_app
from werkzeug.exceptions import HTTPException

def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (best == 'application/json' and
            request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])

def register_error_handlers(app):
    if not app.debug:
        @app.errorhandler(Exception)
        def handle_exception(error):
            if isinstance(error, HTTPException):
                if request_wants_json():
                    return jsonify({
                        'error': error.name,
                        'message': error.description
                    }), error.code
                return render_template(f'errors/{error.code}.html', error=error), error.code

            app.logger.error(f'Unhandled exception: {str(error)}')
            if request_wants_json():
                return jsonify({
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error has occurred'
                }), 500
            return render_template('errors/500.html', error=error), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        if request_wants_json():
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request_wants_json():
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Please authenticate to access this resource'
            }), 401
        return render_template('errors/401.html', error=error), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        if request_wants_json():
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request_wants_json():
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request_wants_json():
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error has occurred'
            }), 500
        return render_template('errors/500.html', error=error), 500 
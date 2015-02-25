from flask_restful import abort

def get_or_404(query, model_id):
    result = query.get(model_id)
    if result == None:
        abort(404, message='Object not found')
    return result
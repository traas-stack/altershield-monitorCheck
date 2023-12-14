from flask_restful import Api
import controllers.detectController as Detect
from flask import Flask
from flask_cors import CORS

# Flask
app = Flask(__name__)
# Cross-domain configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Web api config
api = Api(app)
app.config['JSON_AS_ASCII'] = False
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))

# Service interface
api.add_resource(Detect.BatchMonitorDetectController, '/api/check/batch_monitor_detect',
                 endpoint='detect_controller.batch_monitor_detect')

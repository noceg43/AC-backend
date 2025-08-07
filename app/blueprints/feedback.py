from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for feedbacks
feedbacks_resource = ResourceBlueprint('feedbacks')

# Use the blueprint from the ResourceBlueprint without any overrides
feedbacks_bp = feedbacks_resource.blueprint
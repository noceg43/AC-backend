from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger


# Create a ResourceBlueprint for answers
answers_resource = ResourceBlueprint('answers')

# Use the blueprint from the ResourceBlueprint without any overrides
answers_bp = answers_resource.blueprint
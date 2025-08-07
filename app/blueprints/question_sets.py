from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for question-sets
question_sets_resource = ResourceBlueprint('question-sets')

# Use the blueprint from the ResourceBlueprint without any overrides
question_sets_bp = question_sets_resource.blueprint
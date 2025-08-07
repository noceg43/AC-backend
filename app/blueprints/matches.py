from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for matches
matches_resource = ResourceBlueprint('matches')

# Use the blueprint from the ResourceBlueprint without any overrides
matches_bp = matches_resource.blueprint
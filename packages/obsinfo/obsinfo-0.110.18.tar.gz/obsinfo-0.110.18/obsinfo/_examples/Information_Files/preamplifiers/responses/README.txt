It is redundant to have a Scripps_SPOBS_HydroL22x??_theoretical.stage.yaml
file for each gain, when all that changes is the gain:value and the end of
the description.  Either should allow configureation_definitions in the stage
files as well (or are they already allowed?) or the call to response_stages
in the preamplifier class should have base: and modifier: subsections.

This should be discussed in the documentation.
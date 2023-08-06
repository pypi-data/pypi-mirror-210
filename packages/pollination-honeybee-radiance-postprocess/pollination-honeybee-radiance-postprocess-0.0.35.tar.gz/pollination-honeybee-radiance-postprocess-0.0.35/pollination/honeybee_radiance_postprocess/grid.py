from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class MergeFolderData(Function):
    """Restructure files in a distributed folder."""

    input_folder = Inputs.folder(
        description='Input sensor grids folder.',
        path='input_folder'
    )

    extension = Inputs.str(
        description='Extension of the files to collect data from. It will be ``pts`` '
        'for sensor files. Another common extension is ``ill`` for the results of '
        'daylight studies.'
    )

    dist_info = Inputs.file(
        description='Distribution information file.',
        path='dist_info.json', optional=True
    )

    @command
    def merge_files_in_folder(self):
        return 'honeybee-radiance-postprocess grid merge-folder ./input_folder ' \
            './output_folder {{self.extension}} --dist-info dist_info.json'

    output_folder = Outputs.folder(
        description='Output folder with newly generated files.', path='output_folder'
    )


@dataclass
class MergeFolderMetrics(Function):
    """Restructure annual daylight metrics in a distributed folder."""

    input_folder = Inputs.folder(
        description='Input sensor grids folder.',
        path='input_folder'
    )

    dist_info = Inputs.file(
        description='Distribution information file.',
        path='dist_info.json', optional=True
    )

    grids_info = Inputs.file(
        description='Grid information file.',
        path='grids_info.json', optional=True
    )

    @command
    def merge_metrics_in_folder(self):
        return 'honeybee-radiance-postprocess grid merge-folder-metrics ' \
            './input_folder ./output_folder --dist-info dist_info.json ' \
            '--grids-info grids_info.json'

    output_folder = Outputs.folder(
        description='Output folder with newly generated files.', path='output_folder'
    )

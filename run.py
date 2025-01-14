#run.py
import os
import argparse
import shutil
import sys
from subprocess import call

def run_cmd(command):
    try:
        call(command, shell=True)
    except KeyboardInterrupt:
        print("Process interrupted")
        sys.exit(1)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_image", type=str, default="./test_images/old/a.png", help="Test image")
    parser.add_argument(
        "--output_folder",
        type=str,
        default="./output",
        help="Restored images, please use the absolute path",
    )
    parser.add_argument("--GPU", type=str, default="6,7", help="0,1,2")
    parser.add_argument(
        "--checkpoint_name", type=str, default="Setting_9_epoch_100", help="choose which checkpoint"
    )
    parser.add_argument("--with_scratch", action="store_true")
    parser.add_argument("--HR", action='store_true')
    opts = parser.parse_args()

    gpu1 = opts.GPU

    # resolve relative paths before changing directory
    opts.input_image = os.path.abspath(opts.input_image)
    opts.output_folder = os.path.abspath(opts.output_folder)
    if not os.path.exists(opts.output_folder):
        os.makedirs(opts.output_folder)

    main_environment = os.getcwd()

    ## Stage 1: Overall Quality Improve
    print("Running Stage 1: Overall restoration")
    os.chdir("/usr/src/app/oldphotosource/Global")
    stage_1_input_dir = opts.input_image
    stage_1_output_dir = opts.output_folder

    if not opts.with_scratch:
        stage_1_command = (
            "python3 test.py --test_mode Full --Quality_restore --test_input "
            + stage_1_input_dir
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1
        )
        run_cmd(stage_1_command)
    else:

        mask_dir = os.path.join(stage_1_output_dir, "masks")
        new_input = os.path.join(mask_dir, "input")
        new_mask = os.path.join(mask_dir, "mask")
        stage_1_command_1 = (
            "python3 detection.py --test_path "
            + stage_1_input_dir
            + " --output_dir "
            + mask_dir
            + " --input_size full_size"
            + " --GPU "
            + gpu1
        )

        if opts.HR:
            HR_suffix=" --HR"
        else:
            HR_suffix=""

        stage_1_command_2 = (
            "python3 test.py --Scratch_and_Quality_restore --test_input "
            + new_input
            + " --test_mask "
            + new_mask
            + " --outputs_dir "
            + stage_1_output_dir
            + " --gpu_ids "
            + gpu1 + HR_suffix
        )

        run_cmd(stage_1_command_1)
        run_cmd(stage_1_command_2)

    print("All the processing is done. Please check the results.")

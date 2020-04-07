"""Setup TPC-DS

Colin Dietrich, SADA, 2020
"""

import os
import subprocess
import zipfile
import glob

from google.cloud import storage

import config, gcp_storage


def download_zip():
    """Download the copy of tpcds source.  See README for versioning."""

    client = storage.Client.from_service_account_json(config.gcp_cred_file)
    print("Client created using default project: {}".format(client.project))

    bs = gcp_storage.BlobSync(client=client,
                              bucket_name=config.gcs_zip_bucket,
                              blob_name=config.gcs_ds_zip,
                              local_filepath=config.fp_ds_zip)
    bs.download()

    return bs.local_filepath


def extract_zip():
    """Extract downloaded TPC-DS .zip to the location set in config.fp_ds
    """
    with zipfile.ZipFile(config.fp_ds_zip) as z:
        z.extractall(config.fp_ds)

""" create_makefile filler





























"""


def make_tpcds(verbose=False):
    """Using the installed C compiler, build TPC-DS.  This assumes an
    installed C compiler is available on the host OS.

    Security note: This is also directly running the command line where ever
    config.fp_ds_src is set so be careful.

    Parameters
    ----------
    verbose : bool, print stdout and stderr output
    """
    #subprocess.run(["make", "-C", config.fp_ds_src + config.sep + "tools"])

    cmd = ["make"]
    pipe = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=config.fp_ds_src + config.sep + "tools")

    stdout = pipe.stdout.decode("utf-8")
    stderr = pipe.stderr.decode("utf-8")

    if verbose:
        if len(stdout) > 0:
            print(stdout)
        if len(stderr) > 0:
            print(stderr)

    return stdout, stderr


def run_dsdgen(scale=1, seed=None, verbose=False):
    """Create data for TPC-DS using the binary dsdgen with
    a subprocess for each cpu core on the host machine
    
    Parameters
    ----------
    scale : int, scale factor in GB, acceptable values:
        1, 100, 1000, 10000
    seed : int, random seed value
    verbose : bool, print stdout and stderr output
    """
    if scale not in config.scale_factors:
        raise ValueError("Scale must be one of:", config.scale_factors)

    _data_out = config.fp_ds_data_out + config.sep + str(scale) + "GB"

    cmd = ["./dsdgen", "-DIR", _data_out, "-SCALE", str(scale),
           "-DELIMITER", "|", "-TERMINATE", "N"]

    if seed is not None:
        cmd = cmd + ["-RNGSEED", str(seed)]

    total_cpu = config.cpu_count
    binary_folder = config.fp_ds_src + config.sep + "tools"
    pipe_outputs = []
    stdout = ""
    stderr = ""
    for n in range(1, total_cpu+1):
        child_cpu = str(n)
        total_cpu = str(total_cpu)
        n_cmd = cmd + ["-PARALLEL", total_cpu,
                       "-CHILD", child_cpu]
        pipe = subprocess.run(n_cmd,
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              cwd=binary_folder)
        pipe_outputs.append(pipe)

    for pipe in pipe_outputs:
        stdout += pipe.stdout.decode("utf-8")
        stderr += pipe.stderr.decode("utf-8")

    if verbose:
        if len(stdout) > 0:
            print(stdout)
        if len(stderr) > 0:
            print(stderr)

    return stdout, stderr


def upload_tpc_data_DUP(folder, bucket_name, limit=2000, verbose=False):
    """Upload all data files generated by tpc-ds dsdgen
    
    Parameters
    ----------
    folder : str, absolute path to folder with .dat files
    bucket_name : str, GCS bucket name to upload to
    limit : int, size in MB above which the upload should be skipped
    verbose : bool, print debug and status messages
    
    Returns
    -------
    inventory : list of lists, each item is: 
        [absolute file path, size in MB]
    """
    
    gcs_client = storage.Client.from_service_account_json(config.gcp_cred_file)
    bucket_name = config.gcs_1gb
    
    inventory = []
    
    files = glob.glob(folder)
    for fp in files:
        #table_name = extract_table_name(fp)
        file_name = os.path.basename(fp)
        fp_size = os.path.getsize(fp)/10**6
        if fp_size < limit:

            if verbose:
                print("Uploading {} @ {} MB".format(file_name, fp_size))

            gcs_sync = gcp_storage.BlobSync(client=gcs_client,
                                            bucket_name=bucket_name,
                                            blob_name=file_name,
                                            local_filepath=fp)
            gcs_sync.upload()
            #inventory.append([table_name, file_name, fp])
            inventory.append([file_name, fp])
            if verbose:
                print("...done!")
        elif verbose:
            print("Skipping {} @ {} MB".format(file_name, fp_size))
    return inventory


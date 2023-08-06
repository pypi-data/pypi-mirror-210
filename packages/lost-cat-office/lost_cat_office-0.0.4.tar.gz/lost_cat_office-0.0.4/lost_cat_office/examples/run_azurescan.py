"""A simple module to demostrate how to run the azure scanner
to run it requires the following:
 Env Var
    Name:   AZURE_STORAGE_CONNSTTR
    Value:  <The connection string used to connected to the azure blob storage>
"""
import logging
from datetime import datetime
import os
import multiprocessing as mp
import tempfile
import threading as td

from queue import Empty
from lost_cat.lost_cat import LostCat
from lost_cat_office.processors.azureblob_processor import AzureStorageProcessor

nb_name = "AzureExp"
if not os.path.exists("logs"):
    os.mkdir("logs")

logger = logging.getLogger(__name__)

def loader(uri:str, uriid:int, in_queue: mp.Queue, out_queue: mp.Queue):
    """ Initiate the ABS
        Add the base uri
    """
    try:
        azbc_obj = AzureStorageProcessor()
    except Exception as ex:
        logger.error("Error loading class %s", ex)
        print("Unable to load class!")
        return

    # load the path for the run...
    in_queue.put({"uri": uri, "uriid": -uriid})

    # start the scan
    azbc_obj.in_queue(in_queue=in_queue)
    azbc_obj.out_queue(out_queue=out_queue)
    azbc_obj.scan()
    out_queue.put("DONE")

def lc_reader(out_queue: mp.Queue, settings: dict):
    """Loads up a lost cat instance and will """
    lc = LostCat(paths=settings)
    lc.save_queue(out_queue)
    lc.close()

def reader(out_queue: mp.Queue, filename: str, ):
    idx = 0

    with open(filename, 'w') as fp:
        fp.write("Initilized...\n")
        fp.flush()

        while out_queue:
            try:
            # set a timeout, and handle the semiphore case too
                o_item = out_queue.get(timeout=10) if out_queue else None
                # URIs
                #   -> Metadata
                #   -> Versions
                #       -> metadata
                if o_item == "DONE":
                    break

                # if the user wants to kill the queue if there are not entries...
                # requires timeout set, otherwise the queue get blocks...
                #if not o_item:
                #    break

                logger.debug("Out: %s", o_item)
                idx += 1

                # save the item to the catalog...
                _uri = o_item.get("uri")
                fp.write(o_item)

                # process and do something with the item
                logger.info("URI: %s", _uri)

                if idx % 1000:
                    fp.flush()

            except Empty:
                break

def setup_lc(dbpath: str) -> LostCat:
    """"""
    _db_path = os.path.abspath(dbpath)
    if os.path.exists(_db_path):
        # delete the file
        logger.info("Removing file %s", _db_path)
        os.remove(_db_path)

    _paths = {
        "database": f"sqlite:///{_db_path}" #
    }
    return LostCat(paths=_paths)

def main():
    """initialize and setup a runner to scan an azure isntance"""
    uri = "raw" # <<<< put the path or root name for the blob storate folder here
    db_path = "data/base.db"
    lcpaths = {
        "database": f"sqlite:///{os.path.abspath(db_path)}" #
    }
    lc = setup_lc(dbpath=db_path)

    lc.add_processor(label="Azure Blob",
            base_class=AzureStorageProcessor)
    data = lc.add_source(processor="azurestorageprocessor 0.0.2", uri=uri, isroot=True, overwrite=True)
    # 'uri': 'raw',
    # 'type': 'CLASS:AzureStorageProcessor',
    # 'domain': '<base class>',
    # 'uriid': 1,
    # 'processorid': 1,
    # 'processorname': 'azurestorageprocessor 0.0.2'
    uriid = data.get("uriid",0)
    logger.info("data: %s", data)

    lc.load_db_sources()
    lc.close()

    # now we have a loaded uri...
    # create the queue to read from and load
    in_queue = mp.Queue()
    out_queue = mp.Queue()

    # start this in a thread...
    threads = []

    # the loader class
    threads.append(td.Thread(target=loader, args=[uri, uriid, in_queue, out_queue]))

    # the reader class
    for i in range(5):
    #    threads.append(td.Thread(target=lc.save_queue, args=[out_queue]))
    #    threads.append(td.Thread(target=reader, args=[out_queue, f"data\\oitem{i}.log"]))
        threads.append(td.Thread(target=lc_reader, args=[out_queue, lcpaths]))

    for t in threads:
        t.start()
        t.join()

if __name__ == "__main__":
    """run the processor and process the outputs"""
    _logname = "{}.{}".format(nb_name, datetime.now().strftime("%Y%m%d"))
    logging.basicConfig(filename=f'logs\log.{_logname}.log', level=logging.INFO)
    main()

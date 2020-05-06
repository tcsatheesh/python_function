import logging

import azure.functions as func


def main(inputblob: func.InputStream,
         outputblob: func.Out[func.InputStream]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {inputblob.name}\n"
                 f"Blob Size: {inputblob.length} bytes\n"
                 f"Blob data: {inputblob.read()}")
    outputblob.set(inputblob)

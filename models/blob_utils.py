from __future__ import unicode_literals

import cloudstorage as gcs
import logging
import zipfile

from google.appengine.ext import ndb
from blob_files import BlobFiles

def blob_archive(new_bf=None, archive_path='/'):
    """ bonus: save all BlobFiles in a zip archive """

    @ndb.tasklet
    def callback(bf_key):
        """ key_only query and get() lookup for entity consistency """

        bf = yield bf_key.get_async()
        raise ndb.Return(bf)

    def blobfiles(insert, archive_key):
        """ We do not use ancestor queries. This Generator takes care of index and entity inconsistencies
            https://cloud.google.com/developers/articles/balancing-strong-and-eventual-consistency-with-google-cloud-datastore/
        """

        for bf in BlobFiles.query().filter(BlobFiles.key != archive_key).map(callback, keys_only=True):
            if insert and new_bf.key == bf.key:
                insert = False  # no index inconsistency
            yield bf

        # if the new_bf entity is not yet present in BlobFiles (due to index inconsistencies), it will be inserted here
        if insert:
            yield new_bf

    # add all files to archive, except the archive zipfile itself which has a reserved name (BlobFiles key)
    (archive_folder, _, archive_file) = archive_path

    if new_bf and new_bf.filename != archive_file:

        new_zf = BlobFiles.new(archive_file, folder=archive_folder)
        with gcs.open(new_zf.gcs_filename, 'w', content_type=b'multipart/x-zip',
                      options={b'x-goog-acl': b'public-read', b'cache-control': b'private, max-age=0, no-cache'}) as nzf:

            # nzf is a cloudstorage.storage_api.StreamingBuffer, which can be pickled to append data in a chained task
            with zipfile.ZipFile(nzf, 'w') as zf:
                for each in blobfiles(new_bf is not None, new_zf.key):
                    # We also could have used : each.blob_read()
                    logging.info(each.filename)
                    blob = each.blob_reader().read()
                    zf.writestr(each.filename.encode('utf-8'), blob)

        new_zf.put_async()
    else:
        new_zf = new_bf

    return new_zf
## inbound-email
Example of inbound email on app engine
* Send email with attachment to anything@contactrouter-io.appspotmail.com
* TODO: contactrouter.io mail redirect to contactrouter-io.appspotmail.com
* App Engine posts inbound message and attachment to /_ah/mail/.+ which routes to ```LogSenderHandler(InboundMailHandler)```

```python
class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        """
        :param mail_message: mail message object
        """
        logging.info("Received a message from: " + mail_message.sender)

        # handle attachments
        if hasattr(mail_message, 'attachments'):
            for filename, filecontents in mail_message.attachments:
                logging.info('filename={}'.format(filename))
                bf = BlobFiles.new(filename, folder=GCS_UPLOAD_FOLDER)
                if bf:
                    bf.blob_write(filecontents.decode())
                    bf.put_async()
                    logging.info('Uploaded and saved in default GCS bucket: ' + bf.gcs_filename)

```
* uses cloud storage to save attachments

```python

class BlobFiles(ndb.Model):
    """ Contains GCS files names and serving urls for the app_default_bucket
        GCS files can have a blobkey. A GCS blobkey does NOT have a BlobInfo object.
        A Blobfile entity is like a blobstore.BlobInfo object
    """

    filename = ndb.StringProperty()  # unique (folder not part of filename, key and id)
    extension = ndb.ComputedProperty(lambda self: self.filename.rsplit('.', 1)[1].lower())
    folder = ndb.StringProperty(default='/')
    gcs_filename = ndb.StringProperty(required=True)  # /<bucket></folder[>/self.filename
    blobkey = ndb.ComputedProperty(lambda self: blobstore.create_gs_key('/gs' + self.gcs_filename))
    serving_url = ndb.StringProperty(required=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def new(cls, filename, bucket=None, folder='/'):
        """ filename is the key, which makes an entity unique. But it's not allowed to overwrite a
            BlobFiles entity, if the new gcs_filename is not equal to the existing gcs path
            use_blobstore controls the type of serving_url. True: use Blobkey; False: use gcs_filename
        """

        gcs_filename = '/%s%s/%s' % (bucket or app_identity.get_default_gcs_bucket_name(), folder, filename)
        bf = cls.get_by_id(filename)
        ...
        ...
```
* uses blobstore to serve files
* uses images api to serve images

```python

    def _pre_put_hook(self):
        """ ndb hook to save serving_url """

        if self.extension in ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff', 'ico']:  # image API supported formats
            # High-performance dynamic image serving
            self.serving_url = images.get_serving_url(self.blobkey, secure_url=True)
        elif config.USE_BLOBSTORE:
            # Blobstore: GCS blob keys do not have a BlobInfo filename
            self.serving_url = '/blobserver/%s?save_as=%s' % (self.blobkey, self.filename)
            # bf.serving_url = '/use_blobstore/%s?save_as=%s' % (blobstore.create_gs_key('/gs' + gcs_file_name), bf.filename)
            ...
            ...
            ...
```
            



* test_mail.py script to unit test email and attachment

```sh
Usage: 
test_mail.py urlbase fromaddr toaddr subject body file1 [..filen]

Example:
test_mail.py http://localhost:8080 test@example.com something@appname.appspotmail.com "Sample Subject" "Sample Body" file1.csv file2.csv

        
```
* TODO: saves files based on mail_message properties

### Reference

- [Receiving Email](https://cloud.google.com/appengine/docs/python/mail/receivingmail "Receiving Email") - Google App Engine Python Documentation

  > **Products > Documentation > Google App Engine > Python**
  
  > Email messages sent to your app are implemented as HTTP requests. To process incoming email messages, you associate email addresses with script handlers in your app configuration, then include the handlers in your app's code. Incoming email generates HTTP requests, which are passed to the appropriate scripts.

- https://cloud.google.com/appengine/docs/python/mail/receivingmail
- https://blog.artooro.com/2012/04/04/how-to-handle-incoming-attachments-on-google-app-engine/
- https://gist.github.com/russomi/10d08bfb14841ffbcb55
- Based on https://github.com/voscausa/appengine-gcs-blobstore-python

